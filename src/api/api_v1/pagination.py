"""
Custom pagination classes for JSON:API compliance.
"""
from urllib.parse import urlencode

from django.core.paginator import EmptyPage, PageNotAnInteger
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class JSONAPIPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that follows JSON:API specification.

    This pagination class provides:
    - Data in `data` key as an array of resource objects
    - Pagination links under `links` key: `first`, `last`, `prev`, `next`
    - Pagination meta under `meta` key: `count`, `page`, `pages`, `page_size`
    """

    page_size = 20
    page_size_query_param = "page_size"
    page_query_param = "page"
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return paginated response in JSON:API format.

        Args:
            data: The paginated data

        Returns:
            Response object with JSON:API pagination structure
        """
        # Build pagination links
        links = self._build_pagination_links()

        # Build pagination meta
        meta = self._build_pagination_meta()

        return Response({"links": links, "meta": meta, "data": data})

    def _build_pagination_links(self):
        """
        Build pagination links following JSON:API specification.

        Returns:
            Dictionary containing first, last, prev, and next links
        """
        # Safety check: ensure page exists
        if not hasattr(self, "page") or self.page is None:
            return {
                "first": f"?{self.page_query_param}=1&{self.page_size_query_param}={self.page_size}",
                "last": None,
                "prev": None,
                "next": None,
            }

        # Get the current request from the view context
        request = getattr(self, "request", None)
        if not request:
            # Fallback: return basic links without absolute URLs
            return {
                "first": f"?{self.page_query_param}=1&{self.page_size_query_param}={self.page_size}",
                "last": None,
                "prev": None,
                "next": None,
            }

        try:
            base_url = request.build_absolute_uri()

            # Remove existing pagination parameters
            if "?" in base_url:
                base_url, query_string = base_url.split("?", 1)
                query_params = {}
                for param in query_string.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        if not key.startswith("page") and key != "page_size":
                            query_params[key] = value
                if query_params:
                    base_url += "?" + urlencode(query_params)

            # Build links
            links = {
                "first": f"{base_url}?{self.page_query_param}=1&{self.page_size_query_param}={self.page_size}",
                "last": None,
                "prev": None,
                "next": None,
            }

            # Add last page link
            if self.page.has_other_pages():
                links[
                    "last"
                ] = f"{base_url}?{self.page_query_param}={self.page.paginator.num_pages}&{self.page_size_query_param}={self.page_size}"

            # Add previous page link
            if self.page.has_previous():
                prev_page = self.page.previous_page_number()
                links[
                    "prev"
                ] = f"{base_url}?{self.page_query_param}={prev_page}&{self.page_size_query_param}={self.page_size}"

            # Add next page link
            if self.page.has_next():
                next_page = self.page.next_page_number()
                links[
                    "next"
                ] = f"{base_url}?{self.page_query_param}={next_page}&{self.page_size_query_param}={self.page_size}"

            return links

        except Exception:
            # Fallback: return basic links without absolute URLs
            return {
                "first": f"?{self.page_query_param}=1&{self.page_size_query_param}={self.page_size}",
                "last": None,
                "prev": None,
                "next": None,
            }

    def _build_pagination_meta(self):
        """
        Build pagination meta information.

        Returns:
            Dictionary containing count, page, pages, and page_size
        """
        # Safety check: ensure page exists
        if not hasattr(self, "page") or self.page is None:
            return {"count": 0, "page": 1, "pages": 1, "page_size": self.page_size}

        return {
            "count": self.page.paginator.count,
            "page": self.page.number,
            "pages": self.page.paginator.num_pages,
            "page_size": self.page_size,
        }

    def get_page_size(self, request):
        """
        Get page size from request parameters.

        Args:
            request: The HTTP request

        Returns:
            Page size as integer
        """
        page_size = request.query_params.get(self.page_size_query_param)
        if page_size is not None:
            try:
                page_size = int(page_size)
                if page_size > 0 and page_size <= self.max_page_size:
                    return page_size
            except (ValueError, TypeError):
                pass
        return self.page_size

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate the queryset.

        Args:
            queryset: The queryset to paginate
            request: The HTTP request
            view: The view instance

        Returns:
            Paginated queryset
        """
        # Store the request for use in link building
        self.request = request

        page_size = self.get_page_size(request)
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        try:
            self.page = paginator.page(page_number)
        except PageNotAnInteger:
            self.page = paginator.page(1)
        except EmptyPage:
            self.page = paginator.page(paginator.num_pages)

        if paginator.num_pages > 0 and self.page.number > paginator.num_pages:
            self.page = paginator.page(paginator.num_pages)

        return list(self.page)
