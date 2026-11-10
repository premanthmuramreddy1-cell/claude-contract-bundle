GOAL        Build a working gaming storefront: catalog, search/filter/sort, cart (persisted), checkout with idempotency, a11y + responsive
TIER        T2 (3 files, no deps, no backend — localStorage cart)
BASELINE    main @ working tree
MAP         grep (greenfield)
STEPS
  S1  Token system + layout + catalog render (grid, search, filter, sort)
  S2  Cart drawer (quantities, idempotency key, localStorage) + checkout dialog + toast
ACCEPT      node --check gaming-store/app.js → no output
            verify page loads with 0 console errors at 375/768/1440
RISKIEST    localStorage cart vs checkout consistency — disprove by reloading mid-cart
BUDGET      0 agents · rounds ≤ 1
