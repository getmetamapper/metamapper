
describe("omnisearch.spec.js", () => {
  const workspace = {
    id: "d6acb06747514d17b74f21e7b00c95a4",
    slug: "gcc",
  }

  const member = {
    email: "member.definitions@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    email: "outsider.definitions@metamapper.test",
    password: "password1234",
  }

  describe("search from home page", () => {
    beforeEach(() => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}`))
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", `Search Your Data – ${workspace.slug} – Metamapper`)
    })

    it("displays the searchbox", () => {
      cy.getByTestId("Omnisearch.Searchbox").should("exist")
    })

    it("displays the slogan", () => {
      cy.contains("The search engine for your data").should("be.visible")
    })

    it("can execute a search", () => {
      // Enter a search query...
      cy.getByTestId("Omnisearch.Searchbox").type("employee access tracking{enter}")

      // The page should change...
      cy.location("pathname").should("equal", `/${workspace.slug}/search/results`)
      cy.location("search").should("equal", '?q=employee%20access%20tracking')

      // It should return search results...
      cy.getByTestId("SearchResultItem").should("have.length", 6)
    })
  })

  describe("view search results", () => {
    beforeEach(() => {
      cy.login(member.email, member.password, workspace.id).then(() => {
        cy.visit(`/${workspace.slug}/search/results?q=employee%20access%20tracking`)
        cy.wait(250)
      })
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "employee access tracking – Search – Metamapper")
    })

    it("can navigate through Table search result", () => {
      cy.contains("public.audit_activity").click().then(() => {
        cy.location("pathname")
          .should(
            "equal",
            `/${workspace.slug}/datastores/metamapper/definition/public/audit_activity/overview`
          )

        cy.contains("Properties").should("be.visible")
      })
    })

    it("can navigate through Column search result", () => {
      cy.contains("public.auth_memberships.email").click().then(() => {
        cy.location("pathname")
          .should(
            "equal",
            `/${workspace.slug}/datastores/metamapper/definition/public/auth_memberships/columns`
          )

        cy.contains("Column").should("be.visible")
        cy.contains("Data Type").should("be.visible")
        cy.contains("Nullable").should("be.visible")
      })
    })

    it("can navigate through Comment on Table search result", () => {
      cy.contains("Comment on public.auth_permission").click().then(() => {
        cy.location("pathname")
          .should(
            "equal",
            `/${workspace.slug}/datastores/metamapper/definition/public/auth_permission/overview`
          )

        cy.contains("Permissions that an employee has in Metamapper.").should("be.visible")
      })
    })

    it("can navigate through Comment on Column search result", () => {
      cy.contains("Comment on public.votes.user_id").click().then(() => {
        cy.location("pathname")
          .should(
            "equal",
            `/${workspace.slug}/datastores/metamapper/definition/public/votes/columns`
          )

        cy.location("search").should("equal", "?selectedColumn=hrzuBCzQDQ5U")

        cy.contains("The employee that made the action.").should("be.visible")
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/search"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("for search page", () => {
      cy.login(outsider.email, outsider.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/search`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("for search results", () => {
      cy.login(outsider.email, outsider.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/search/results`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
