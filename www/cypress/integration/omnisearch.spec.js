import { DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("omnisearch.spec.js", () => {
  describe("search from home page", () => {
    beforeEach(() => {
      cy.quickLogin("owner").then(() => cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/`)).then(() => cy.reload())
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", `Search Your Data – ${DEFAULT_WORKSPACE_SLUG} – Metamapper`)
    })

    it("displays the searchbox", () => {
      cy.getByTestId("Omnisearch.Searchbox").should("exist")
    })

    it("displays the slogan", () => {
      cy.contains("The search engine for your data").should("be.visible")
    })

    it("can execute a search", () => {
      // Enter a search query...
      cy.getByTestId("Omnisearch.Searchbox").type("customer order forms{enter}")

      // The page should change...
      cy.location("pathname").should("equal", `/${DEFAULT_WORKSPACE_SLUG}/search/results`)
      cy.location("search").should("equal", '?q=customer%20order%20forms')

      // It should return search results...
      cy.getByTestId("SearchResultItem").should("have.length", 15)
    })
  })

  describe("view search results", () => {
    beforeEach(() => {
      cy.quickLogin("owner").then(() => {
        cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/search/results?q=customer%20order%20forms`)
        cy.wait(500)
      })
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", `customer order forms – Search – Metamapper`)
    })

    it("can navigate through Table search result", () => {
      cy.contains("app.orders").click().then(() => {
        cy.location("pathname")
          .should(
            "equal",
            `/${DEFAULT_WORKSPACE_SLUG}/datastores/metamapper/definition/app/orders/overview`
          )

        cy.contains("Properties").should("be.visible")
      })
    })

    it("can navigate through Column search result", () => {
      cy.contains("app.payments.customernumber").click().then(() => {
        cy.location("pathname")
          .should(
            "equal",
            `/${DEFAULT_WORKSPACE_SLUG}/datastores/metamapper/definition/app/payments/columns`
          )

        cy.contains("Column").should("be.visible")
        cy.contains("Data Type").should("be.visible")
        cy.contains("Nullable").should("be.visible")
      })
    })

    it("can navigate through Comment search result", () => {
      cy.contains("Comment on app.orderdetails.quantityordered").click().then(() => {
        cy.location("pathname")
          .should(
            "equal",
            `/${DEFAULT_WORKSPACE_SLUG}/datastores/metamapper/definition/app/orderdetails/columns`
          )

        cy.location("search").should("equal", "?selectedColumn=UOA8JNoQIhNy")

        cy.contains("The number of items ordered by the customer.").should("be.visible")
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login("member@metamapper.io", "password1234")
        .then(() =>
          cy.visit("/does-not-exist/search"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("for search page", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/search`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("for search results", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/search/results`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
