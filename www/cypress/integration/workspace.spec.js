import { WORKSPACE_TOKEN } from "../../src/lib/constants"
import { DEFAULT_WORKSPACE_ID, DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("workspace.spec.js", () => {
  describe("list user workspaces", () => {
    beforeEach(() => {
      cy.quickLogin("owner").then(() => cy.visit("/workspaces"))
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Workspaces - Metamapper")
    })

    it("displays a list of workspaces that the user belongs to", () => {
      cy.getByTestId("WorkspaceList")
        .should("exist")
        .and("contain", "Dunder Mifflin")
        .and("contain", "Cress Tool & Die")
        .and("contain", "Vance Refrigeration")
        .and("not.contain", "Acme Corporation");
    })

    it("navigates to a workspace when clicked", () => {
      cy.getByTestId("WorkspaceList")
        .contains("Vance Refrigeration")
        .click()

      cy.location("pathname").should("equal", "/VanceRefrigeration")

      cy.wait(1000)
        .then(() => {
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.be.a("string")
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.not.equal(DEFAULT_WORKSPACE_ID)
        })

      cy.getByTestId("Navbar.Dropdown").click()

      cy.contains("Manage Workspace")
        .should("have.attr", "href")
        .and("include", "VanceRefrigeration")
    })
  })

  describe("create a workspace", () => {
    beforeEach(() => {
      cy.login().then(() => cy.visit("/"))
      cy.visit("/workspaces")
    })

    it("fails with an incorrectly formatted slug", () => {
      cy.contains("Create New Workspace").click()

      cy.fillInputs({
        "WorkspaceSetupForm.Name": "Pysch",
        "WorkspaceSetupForm.Slug": "psych santa barbara",
      })

      cy.getByTestId("WorkspaceSetupForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(
        ".ant-message-error",
        "Workspace slug is improperly formatted."
      ).should(
        "be.visible"
      )
    })

    it("fails with an existing slug", () => {
      cy.contains("Create New Workspace").click()

      cy.fillInputs({
        "WorkspaceSetupForm.Name": "Pysch",
        "WorkspaceSetupForm.Slug": "dunder-mifflin",
      })

      cy.getByTestId("WorkspaceSetupForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(
        ".ant-message-error",
        "A workspace already exists with that slug."
      ).should(
        "be.visible"
      )
    })

    it("using UI", () => {
      cy.contains("Create New Workspace").click()

      cy.fillInputs({
        "WorkspaceSetupForm.Name": "Psych",
        "WorkspaceSetupForm.Slug": "psych",
      })

      cy.getByTestId("WorkspaceSetupForm.Submit").click()

      // It should re-direct to the datastores page since no datastores exist.
      cy.location("pathname").should("equal", "/psych")

      cy
        .then(() => {
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.be.a("string")
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.not.equal(DEFAULT_WORKSPACE_ID)
        })
    })
  })

  const existedSlug = "VanceRefrigeration"
  const updatedSlug = "sabre"
  const workspaceId = "bcb8e056-40eb-460f-8326-eebfd9d7a1e2"

  describe("update a workspace", () => {
    it("fails when user does not have permission", () => {
      cy.login("member@metamapper.io", "password1234", DEFAULT_WORKSPACE_ID)
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings`))

      cy.formIsDisabled("UpdateWorkspaceForm")
    })

    it("fails with an incorrectly formatted slug", () => {
      cy.login("owner@metamapper.io", "password1234", workspaceId)
        .then(() =>
          cy.visit(`/${existedSlug}/settings`))

      cy.fillInputs({
        "UpdateWorkspaceForm.Slug": "glass half full"
      })

      cy.getByTestId("UpdateWorkspaceForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(
        ".ant-message-error",
        "Workspace slug is improperly formatted."
      ).should(
        "be.visible"
      )
    })

    it("using UI (as workspace owner)", () => {
      cy.login("owner@metamapper.io", "password1234", workspaceId)
        .then(() =>
          cy.visit(`/${existedSlug}/settings`))

      cy.fillInputs({
        "UpdateWorkspaceForm.Name": "Sabre Printers",
        "UpdateWorkspaceForm.Slug": updatedSlug,
      })

      cy.getByTestId("UpdateWorkspaceForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Workspace has been updated.").should(
        "be.visible"
      )
    })
  })

  describe("delete a workspace", () => {
    it("with readonly permissions", () => {
      cy.quickLogin("readonly")
        .then(() => cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings`))
        .then(() => cy.reload())

      cy.formIsDisabled("DeleteWorkspace")
    })

    it("with basic permissions", () => {
      cy.quickLogin("member")
        .then(() => cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings`))
        .then(() => cy.reload())

      cy.formIsDisabled("DeleteWorkspace")
    })

    it("requires the correct confirmation prompt", () => {
      cy.login("owner@metamapper.io", "password1234", workspaceId)
        .then(() =>
          cy.visit(`/${updatedSlug}/settings`).wait(500))

      cy.getByTestId("DeleteWorkspace.Open").click()

      cy.fillInputs({
        "DeleteWorkspace.ConfirmationPrompt": "incorrect"
      })

      cy.getByTestId("DeleteWorkspace.Submit").should("be.disabled")
    })

    it("with owner permissions", () => {
      cy.login("owner@metamapper.io", "password1234", workspaceId)
        .then(() =>
          cy.visit(`/${updatedSlug}/settings`))

      cy.getByTestId("DeleteWorkspace.Open").click()

      cy.fillInputs({
        "DeleteWorkspace.ConfirmationPrompt": "delete me"
      })

      cy.getByTestId("DeleteWorkspace.Submit").click()

      cy.location("pathname").should("equal", "/workspaces")

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Workspace has been deleted.").should(
        "be.visible"
      )

      cy.getByTestId("WorkspaceList")
        .should("exist")
        .and("not.contain", "Vance Refrigeration")
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit("/does-not-exist/settings"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit(`/${existedSlug}/settings`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
