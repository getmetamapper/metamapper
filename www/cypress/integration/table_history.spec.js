
describe("table_history.spec.js", () => {
  const workspace = {
    id: "d6acb06747514d17b74f21e7b00c95a4",
    slug: "gcc",
  }

  const owner = {
    email: "owner.definitions@metamapper.test",
    password: "password1234",
  }

  const member = {
    email: "member.definitions@metamapper.test",
    password: "password1234",
  }

  const readonly = {
    email: "readonly.definitions@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    email: "outsider.definitions@metamapper.test",
    password: "password1234",
  }

  const datastore = {
    name: "Metamapper",
    slug: "metamapper",
  }

  const table = {
    schema: "public",
    name: "definitions_table",
  }

  const databaseUri = `/${workspace.slug}/datastores/${datastore.slug}`
  const overviewUri = `${databaseUri}/definition/${table.schema}/${table.name}/history`

  describe("view", () => {
    before(() => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() => cy.visit(overviewUri))
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", `History - ${table.schema}.${table.name} - ${datastore.slug} - Metamapper`)
    })

    it("renders the revisions table", () => {
      cy.getByTestId("TableRevisionLog").should("exist").find("tbody").find("tr").its("length").should("be.gte", 10)
    })

    it("renders some activities", () => {
      cy.getByTestId("TableRevisionLog")
        .should("contain", "Table public.definitions_table was added.")
        .should("contain", "Column definitions_table.kind was added.")
        .should("contain", "Column definitions_table.deleted_at was added.")
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/datastores/show-me/definition/potato/salad/history"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when datastore does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/show-me/definition/potato/salad/history`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when table definition does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/${datastore.slug}/definition/potato/salad/history`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
