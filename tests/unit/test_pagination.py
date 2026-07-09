import pytest

from bcic.exceptions import PaginationLimitError, ValidationError
from bcic.models import Page, PageMetadata
from bcic.pagination import traverse_pages


def page(start: int, items: list[int], *, has_more: bool | None = None) -> Page[int]:
    return Page[int](
        items=items,
        metadata=PageMetadata(
            page=(start // 2) + 1,
            page_size=2,
            start_row=start,
            returned_count=len(items),
            has_more=has_more,
        ),
    )


def test_traversal_stops_on_empty_short_and_authoritative_completion() -> None:
    assert (
        traverse_pages(
            lambda offset: page(offset, []), page_size=2, max_pages=2, max_items=4
        )
        == []
    )
    assert traverse_pages(
        lambda offset: page(offset, [1]), page_size=2, max_pages=2, max_items=4
    ) == [1]
    assert traverse_pages(
        lambda offset: page(offset, [1, 2], has_more=False),
        page_size=2,
        max_pages=2,
        max_items=4,
    ) == [1, 2]


def test_traversal_detects_non_advancing_page_metadata() -> None:
    with pytest.raises(ValidationError):
        traverse_pages(
            lambda offset: page(0, [1, 2]),
            page_size=2,
            max_pages=2,
            max_items=4,
        )


@pytest.mark.parametrize(
    ("page_size", "max_pages", "max_items"), [(0, 1, 1), (1, 0, 1), (1, 1, 0)]
)
def test_traversal_validates_limits_before_fetch(
    page_size: int, max_pages: int, max_items: int
) -> None:
    called = False

    def fetch(offset: int) -> Page[int]:
        nonlocal called
        called = True
        return page(offset, [])

    with pytest.raises(ValidationError):
        traverse_pages(
            fetch,
            page_size=page_size,
            max_pages=max_pages,
            max_items=max_items,
        )

    assert called is False


def test_traversal_does_not_replay_successful_pages_after_failure() -> None:
    offsets: list[int] = []

    def fetch(offset: int) -> Page[int]:
        offsets.append(offset)
        if offset == 2:
            raise RuntimeError("failed page")
        return page(offset, [1, 2])

    with pytest.raises(RuntimeError):
        traverse_pages(fetch, page_size=2, max_pages=3, max_items=6)

    assert offsets == [0, 2]


def test_traversal_raises_item_limit_without_returning_partial_data() -> None:
    with pytest.raises(PaginationLimitError):
        traverse_pages(
            lambda offset: page(offset, [1, 2]),
            page_size=2,
            max_pages=2,
            max_items=1,
        )
