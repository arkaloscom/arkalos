import React from 'react'
import { useSearchParams, useLocation, Link } from 'react-router'

export default function Pagination({ total_pages }) {
  const [searchParams] = useSearchParams()
  const location = useLocation()
  const maxPagesToShow = 19

  const currentPage = parseInt(searchParams.get('page') || '1', 10)

  const { startPage, endPage } = calculatePageRange()

  const prevPage = currentPage - 1
  const nextPage = currentPage + 1

  const prevSearchString = getPageSearchString(prevPage)
  const nextSearchString = getPageSearchString(nextPage)

  const prevLinkTo = { pathname: location.pathname, search: prevSearchString }
  const nextLinkTo = { pathname: location.pathname, search: nextSearchString }

  const isFirstPage = currentPage === 1
  const isLastPage = currentPage === total_pages

  function getPageSearchString(page) {
    const newSearchParams = new URLSearchParams(searchParams)
    if (page > 1) {
      newSearchParams.set('page', page.toString())
    } else {
      newSearchParams.delete('page')
    }
    const searchString = newSearchParams.toString()
    return searchString ? `?${searchString}` : ''
  }

  function calculatePageRange() {
    let startPage, endPage

    if (total_pages <= maxPagesToShow) {
      startPage = 1
      endPage = total_pages
    } else {
      const halfMaxPages = Math.floor(maxPagesToShow / 2)

      if (currentPage <= halfMaxPages + 1) {
        startPage = 1
        endPage = maxPagesToShow
      } else if (currentPage >= total_pages - halfMaxPages) {
        startPage = total_pages - maxPagesToShow + 1
        endPage = total_pages
      } else {
        startPage = currentPage - halfMaxPages
        endPage = currentPage + halfMaxPages
      }
    }
    return { startPage, endPage }
  }

  function renderItem(pageNr) {
    const isActive = pageNr === currentPage
    const itemSearchString = getPageSearchString(pageNr)
    const itemTo = { pathname: location.pathname, search: itemSearchString }

    return (
      <Link to={itemTo} aria-current={isActive ? 'page' : undefined}>
        {pageNr}
      </Link>
    )
  }

  function renderItems(start, end) {
    const results = []
    for (let k = start; k <= end; k++) {
      results.push(renderItem(k))
    }
    return results
  }

  function renderPrev() {
    if (isFirstPage) {
      return (
        <Link to={null} aria-disabled="true">
          &laquo; Previous
        </Link>
      )
    }
    return (
      <Link to={prevLinkTo} aria-label="Previous Page" aria-disabled={isFirstPage ? true : null}>
        &laquo; Previous
      </Link>
    )
  }

  function renderNext() {
    if (isLastPage) {
      return (
        <Link to={null} aria-disabled="true">
          Next &raquo;
        </Link>
      )
    }
    return (
      <Link to={nextLinkTo} aria-label="Next Page" aria-disabled={isLastPage ? true : null}>
        Next &raquo;
      </Link>
    )
  }

  if (total_pages <= 0) {
    return
  }

  return (
    <>
      <nav aria-label="pagination">
        {renderPrev()}
        {renderItems(startPage, endPage)}
        {renderNext()}
      </nav>
    </>
  )
}
