
describe("table_owners.spec.js", () => {
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
    name: "audit_activity",
  }

  const databaseUri = `/${workspace.slug}/datastores/${datastore.slug}`
  const overviewUri = `${databaseUri}/definition/${table.schema}/${table.name}/overview`

  const existingOwners = [
    {
      id: 'QXNzZXRPd25lclR5cGU6MQ==',
      name: "Jeff Winger",
    },
    {
      id: 'QXNzZXRPd25lclR5cGU6Mg==',
      name: "Analytics",
    },
  ]

  // Tests for the basic UI components of this page.
  describe("overview", () => {
    before(() => {
      cy.login(member.email, member.password, workspace.id)
        .then(() => cy.visit(overviewUri))
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", `Overview - ${table.schema}.${table.name} - ${datastore.slug} - Metamapper`)
    })

    it("displays the existing owners", () => {
      cy.getByTestId("TableOwners").should("be.visible")
      cy.getByTestId("TableOwners").get(".table-owner").should("have.length", 2)

      existingOwners.forEach(({ id, name }) => {
        cy.getByTestId(`TableOwner.Item(${id})`).should("be.visible").contains(name)
      })
    })
  })

  describe("as readonly", () => {
    beforeEach(() => {
      cy.login(readonly.email, readonly.password, workspace.id)
        .then(() => cy.visit(overviewUri))
    })

    it("cannot see create or edit buttons", () => {
      cy.getByTestId("TableOwnersHeader.Edit").should("not.be.visible")
      cy.getByTestId("TableOwnersHeader.Add").should("not.be.visible")
    })
  })

  describe("create new owner", () => {
    beforeEach(() => {
      cy.login(member.email, member.password, workspace.id)
        .then(() => cy.visit(overviewUri))
    })

    it("can toggle the prompt", () => {
      cy.getByTestId("CreateAssetOwner.Input").should("not.be.visible")

      // Initial fill out ...
      cy.getByTestId("TableOwnersHeader.Add").click()
      cy.getByTestId("CreateAssetOwner.Input").get(".ant-select-selection").type("Shirle")
      cy.contains("Shirley Bennett").click()
      cy.getByTestId("CreateAssetOwner.Input").contains("Shirley").should("be.visible")

      // Toggle off
      cy.getByTestId("TableOwnersHeader.Add").click()
      cy.getByTestId("CreateAssetOwner.Input").should("not.be.visible")

      // Confirm it cleared
      cy.getByTestId("TableOwnersHeader.Add").click()
      cy.getByTestId("CreateAssetOwner.Input").contains("Shirley").should("not.exist")
    })

    it("using UI", () => {
      cy.getByTestId("TableOwnersHeader.Add").click()
      cy.getByTestId("CreateAssetOwner.Input").get(".ant-select-selection").type("Shirle")

      cy.contains("Shirley Bennett").click()
      cy.getByTestId("CreateAssetOwner.Submit").click()

      cy.getByTestId("TableOwners").contains("Shirley Bennett")
      cy.getByTestId("TableOwners").get(".table-owner").should("have.length", 3)
    })
  })

  describe("update owner", () => {
    beforeEach(() => {
      cy.login(member.email, member.password, workspace.id)
        .then(() => cy.visit(overviewUri))
    })

    it("see create edit buttons", () => {
      cy.getByTestId("TableOwnersHeader.Edit").should("be.visible")
    })
  })

  describe("remove owner", () => {
    beforeEach(() => {
      cy.login(member.email, member.password, workspace.id)
        .then(() => cy.visit(overviewUri))
    })

    it("using UI", () => {
      cy.getByTestId("TableOwnersHeader.Edit").click()

      existingOwners.forEach(({ id, name }, idx) => {
        cy.getByTestId(`TableOwner.Item(${id})`).within(() => cy.getByTestId("DeleteAssetOwner.Submit").click())

        cy.get(".ant-popover-content")
          .should("be.visible")
          .within(() => cy.contains("Yes").click())

        cy.getByTestId("TableOwners").get(".table-owner").should("have.length", existingOwners.length - idx)
      })

      // Delete the owner we created in the previous test...
      cy.getByTestId("DeleteAssetOwner.Submit").click()
      cy.get(".ant-popover-content")
        .should("be.visible")
        .within(() => cy.contains("Yes").click())

      cy.getByTestId("TableOwners").get(".table-owner").should("have.length", 0)
      cy.getByTestId("TableOwners").contains("No owners assigned.")
    })
  })
})

