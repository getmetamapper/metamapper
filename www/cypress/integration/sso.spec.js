import { DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("sso.spec.js", () => {
  before(() => {
    cy.resetdb()
  })

  let doesNotHavePermission = ["readonly", "member"]

  describe("list of connections", () => {
    before(() => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))
    })

    it("displays the right meta title", () => {
      cy.title().should("eq", `Authentication - ${DEFAULT_WORKSPACE_SLUG} - Metamapper`)
    })

    it("displays a list of domains", () => {
      cy.getByTestId("SSODomainsTable").should("exist")

      cy.getByTestId("SSODomainsTable").within(() => {
        cy.getByTestId("SSODomainsTable.VerificationStatus").should("have.length", 2)
      })
    })
  })

  describe("create connection", () => {
    doesNotHavePermission.forEach((permission) => {
      it(`fails with ${permission} permission`, () => {
        cy.quickLogin(permission)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

        cy.contains("Connections").should("be.visible")
        cy.getByTestId("SSODomainsTable").should("exist")
        cy.contains("Add New Connection").should("not.be.visible")
      })
    })
  })

  describe("set default connection", () => {
    doesNotHavePermission.forEach((permission) => {
      it(`fails with ${permission} permission`, () => {
        cy.quickLogin(permission)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

        cy.contains("Connections").should("be.visible")
        cy.getByTestId("SSODomainsTable").should("exist")

        cy.formIsDisabled("SetDefaultSSOConnectionForm", [
          "Input",
          "Submit",
        ])
      })
    })

    it("succeeds with valid permission", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

      cy.fillInputs({
        "SetDefaultSSOConnectionForm.Input": "Xm3F2M3RRJpO"
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
    doesNotHavePermission.forEach((permission) => {
      it(`fails with ${permission} permission`, () => {
        cy.quickLogin(permission)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

        cy.contains("Connections").should("be.visible")
        cy.getByTestId("SSODomainsTable").should("exist")
        cy.getByTestId("DeleteSSOConnection.Submit").should("be.disabled")
      })
    })

    it("fails with default connection", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

      // We set this audience to the default in a previous test...
      let defaultAudience = "urn:saml2:metamapper:generic-Xm3F2M3RRJpO"

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
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

      let deletedAudience = "urn:saml2:metamapper:generic-k54Me1G77SnX"

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
    doesNotHavePermission.forEach((permission) => {
      it(`fails with ${permission} permission`, () => {
        cy.quickLogin(permission)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

        cy.formIsDisabled("SSODomainSetupForm", [
          "Domain",
          "Submit",
        ])
      })
    })

    beforeEach(() => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))
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
    doesNotHavePermission.forEach((permission) => {
      it(`fails with ${permission} permission`, () => {
        cy.quickLogin(permission)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

        cy.getByTestId("DeleteSSODomain.Submit").should("be.disabled").contains("Remove")
      })
    })

    it("succeeds with valid permission", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

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
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit("/does-not-exist/settings/authentication"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/authentication`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
