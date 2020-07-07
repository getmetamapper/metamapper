
describe("sso.spec.js", () => {

  const workspace = {
    id: "7fdeecda-18bb-4592-a5d1-e00f18739d02",
    name: "The Pussycats",
    slug: "josie-and-the-pussycats",
  }

  const otherWorkspace = {
    id: "dc909e3d-e10d-4904-ac4c-cf1c567fe211",
    name: "DuJour",
    slug: "DuJour",
  }

  const owner = {
    email: "owner.sso@metamapper.test",
    password: "password1234",
  }

  const member = {
    email: "member.sso@metamapper.test",
    password: "password1234",
  }

  const readonly = {
    email: "readonly.sso@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    email: "outsider.sso@metamapper.test",
    password: "password1234",
  }

  const defaultConnectionId = "uayGFt47yvTA"
  const anotherConnectionId = "VaH1hwOlI0RI"

  const doesNotHavePermission = [
    { permission: "member", user: member },
    { permission: "readonly", user: readonly },
  ]

  describe("list of connections", () => {
    before(() => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/authentication`))
    })

    it("displays the right meta title", () => {
      cy.title().should("eq", `Authentication - ${workspace.slug} - Metamapper`)
    })

    it("displays a list of connections", () => {
      cy.getByTestId("SSOConnectionsTable").should("exist")
      cy.getByTestId("SSOConnectionsTable.Name").should("have.length", 2)
    })
  })

  describe("create connection", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      beforeEach(() => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/authentication`))
      })

      it(`fails with ${permission} permission`, () => {
        cy.contains("Connections").should("be.visible")
        cy.getByTestId("SSODomainsTable").should("exist")
        cy.contains("Add New Connection").should("not.be.visible")
      })
    })
  })

  describe("set default connection", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      beforeEach(() => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/authentication`))
      })

      it(`fails with ${permission} permission`, () => {
        cy.contains("Connections").should("be.visible")
        cy.getByTestId("SSODomainsTable").should("exist")

        cy.formIsDisabled("SetDefaultSSOConnectionForm", [
          "Input",
          "Submit",
        ])
      })
    })

    it("succeeds with valid permission", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/authentication`))

      cy.fillInputs({
        "SetDefaultSSOConnectionForm.Input": defaultConnectionId
      })

      cy.getByTestId("SetDefaultSSOConnectionForm.Submit").click()

      cy.contains(
        ".ant-message-success", "Default connection has been updated."
      ).should(
        "be.visible"
      )
    })
  })

  describe("remove connection", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      beforeEach(() => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/authentication`))
      })

      it(`fails with ${permission} permission`, () => {
        cy.contains("Connections").should("be.visible")
        cy.getByTestId("SSODomainsTable").should("exist")
        cy.getByTestId("DeleteSSOConnection.Submit").should("be.disabled")
      })
    })

    it("fails with default connection", () => {
      // We set this audience to the default in a previous test...
      let defaultAudience = `urn:saml2:metamapper:generic-${defaultConnectionId}`

      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/authentication`))

      cy.getByTestId("SSOConnectionsTable").contains(defaultAudience).parent("tr").within(() => {
        cy.getByTestId("DeleteSSOConnection.Submit").click()
      })

      cy.get(".ant-popover-buttons").contains("Yes").click()

      cy.contains(
        ".ant-message-error", "You cannot delete the default connection."
      ).should(
        "be.visible"
      )

      cy.getByTestId("SSOConnectionsTable").should("exist").and("contain", defaultAudience)
    })

    it("succeeds with valid permission", () => {
      let deletedAudience = `urn:saml2:metamapper:generic-${anotherConnectionId}`

      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/authentication`))

      cy.getByTestId("SSOConnectionsTable").contains(deletedAudience).parent("tr").within(() => {
        cy.getByTestId("DeleteSSOConnection.Submit").click()
      })

      cy.get(".ant-popover-buttons").contains("Yes").click()

      cy.contains(
        ".ant-message-success", "Connection has been removed."
      ).should(
        "be.visible"
      )

      cy.getByTestId("SSOConnectionsTable").should("exist").and("not.contain", deletedAudience)
    })
  })

  describe("create domain", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      it(`fails with ${permission} permission`, () => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/authentication`))

        cy.formIsDisabled("SSODomainSetupForm", [
          "Domain",
          "Submit",
        ])
      })
    })

    beforeEach(() => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/authentication`))
    })

    it("fails with improperly formatted domain", () => {
      cy.fillInputs({
        "SSODomainSetupForm.Domain": "127.0.0.1"
      })

      cy.getByTestId("SSODomainSetupForm.Submit").click()

      cy.contains(
        ".ant-message-error", "Domain is not valid."
      ).should(
        "be.visible"
      )
    })

    it("fails with a domain that is already claimed", () => {
      cy.fillInputs({
        "SSODomainSetupForm.Domain": "metamapper.dev"
      })

      cy.getByTestId("SSODomainSetupForm.Submit").click()

      cy.contains(
        ".ant-message-error", "Domain has already been claimed."
      ).should(
        "be.visible"
      )
    })

    it("succeeds with valid domain", () => {
      cy.fillInputs({
        "SSODomainSetupForm.Domain": "metamapper.io"
      })

      cy.getByTestId("SSODomainSetupForm.Submit").click()

      cy.contains(
        ".ant-message-success", "Domain has been added and is pending verification."
      ).should(
        "be.visible"
      )

      cy.getByTestId("SSODomainsTable").contains("metamapper.io").parent("tr").within(() => {
        cy.get("td").eq(2).contains("PENDING")
      })
    })
  })

  describe("remove domain", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      beforeEach(() => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/authentication`))
      })

      it(`fails with ${permission} permission`, () => {
        cy.getByTestId("DeleteSSODomain.Submit").should("be.disabled").contains("Remove")
      })
    })

    it("succeeds with valid permission", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/authentication`))

      let deletedDomain = "metamapper.net"

      cy.getByTestId("SSODomainsTable").contains(deletedDomain).parent("tr").within(() => {
        cy.getByTestId("DeleteSSODomain.Submit").click()
      })

      cy.get(".ant-popover-buttons").contains("Yes").click()

      cy.contains(
        ".ant-message-success", "Domain has been removed."
      ).should(
        "be.visible"
      )

      cy.getByTestId("SSODomainsTable").should("exist").and("not.contain", deletedDomain)
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/settings/authentication"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(`/${otherWorkspace.slug}/settings/authentication`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
