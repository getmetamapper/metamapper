import { WORKSPACE_TOKEN } from "../../src/lib/constants"

describe("workspace.spec.js", () => {
  // Fixtures...
  const primaryWorkspace = {
    id: "301ccdfe-12d7-49e8-854f-5da614224e7e",
    name: "Rocinante",
    slug: "roci",
  }

  // This workspace is eventually deleted, so don't change the attributes.
  const secondaryWorkspace = {
    id: "0027d5fe-26a6-4929-9c0f-b312f0395a27",
    name: "Ceres",
    slug: "ceres12345",
  }

  // The team does not have access to this workspace.
  const privateWorkspace = {
    id: "634cb29e-5ff3-4375-8a0b-f9481bf41d0d",
    name: "MCRN Donnager",
    slug: "MCRN-Donnager",
  }

  const newWorkspace = {
    name: "Canterbury",
    slug: "the-canterbury",
  }

  const owner = {
    fname: "Naomi",
    lname: "Nagata",
    email: "owner.workspace@metamapper.test",
    password: "password1234",
  }

  const member = {
    fname: "Amos",
    lname: "Burton",
    email: "member.workspace@metamapper.test",
    password: "password1234",
  }

  const readonly = {
    fname: "James",
    lname: "Holden",
    email: "readonly.workspace@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    fname: "Camina",
    lname: "Drummer",
    email: "outsider.workspace@metamapper.test",
    password: "password1234",
  }

  describe("list user workspaces", () => {
    beforeEach(() => {
      cy.login(owner.email, owner.password, primaryWorkspace.id).then(() => cy.visit('/workspaces'))
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Workspaces - Metamapper")
    })

    it("displays a list of workspaces that the user belongs to", () => {
      cy.getByTestId("WorkspaceList")
        .should("exist")
        .and("contain", primaryWorkspace.name)
        .and("contain", secondaryWorkspace.name)
        .and("not.contain", privateWorkspace.name)
    })

    it("navigates to a workspace when clicked", () => {
      cy.getByTestId("WorkspaceList").contains(secondaryWorkspace.name).click()

      cy.location("pathname").should("equal", `/${secondaryWorkspace.slug}`)

      cy.wait(1000)
        .then(() => {
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.be.a("string")
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.equal(secondaryWorkspace.id)
        })

      cy.getByTestId("Navbar.Dropdown").click()

      cy.contains("Manage Workspace").should("have.attr", "href").and("include", secondaryWorkspace.slug)
    })
  })

  describe("create a workspace", () => {
    beforeEach(() => {
      cy.login(member.email, member.password, primaryWorkspace.id).then(() => cy.visit('/workspaces'))
    })

    it("fails with an incorrectly formatted slug", () => {
      cy.contains("Create New Workspace").click()

      cy.fillInputs({
        "WorkspaceSetupForm.Name": newWorkspace.name,
        "WorkspaceSetupForm.Slug": "this is invalid",
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
        "WorkspaceSetupForm.Name": newWorkspace.name,
        "WorkspaceSetupForm.Slug": primaryWorkspace.slug,
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
        "WorkspaceSetupForm.Name": newWorkspace.name,
        "WorkspaceSetupForm.Slug": newWorkspace.slug,
      })

      cy.getByTestId("WorkspaceSetupForm.BeaconConsent").should("be.visible").should("not.have.class", "ant-switch-checked")
      cy.getByTestId("WorkspaceSetupForm.Submit").click()

      // It should re-direct to the datastores page since no datastores exist.
      cy.location("pathname").should("equal", `/${newWorkspace.slug}/datastores/new`)

      cy.wait(1000)
        .then(() => {
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.be.a("string")
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.not.equal(primaryWorkspace.id)
        })
    })
  })

  describe("update a workspace", () => {
    it("fails when user does not have permission", () => {
      cy.login(member.email, member.password, primaryWorkspace.id)
        .then(() =>
          cy.visit(`/${primaryWorkspace.slug}/settings`))

      cy.formIsDisabled("UpdateWorkspaceForm")
    })

    it("fails with an incorrectly formatted slug", () => {
      cy.login(owner.email, owner.password, primaryWorkspace.id)
        .then(() =>
          cy.visit(`/${primaryWorkspace.slug}/settings`))

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

    it("using UI", () => {
      cy.login(owner.email, owner.password, primaryWorkspace.id)
        .then(() =>
          cy.visit(`/${primaryWorkspace.slug}/settings`))

      cy.fillInputs({
        "UpdateWorkspaceForm.Name": "MCRN Tachi",
        "UpdateWorkspaceForm.Slug": "Tachi",
      })

      cy.getByTestId("UpdateWorkspaceForm.BeaconConsent").should("be.visible").click()
      cy.getByTestId("UpdateWorkspaceForm.BeaconConsent").should("have.class", "ant-switch-checked")

      cy.getByTestId("UpdateWorkspaceForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(
        ".ant-message-success",
        "Workspace has been updated."
      ).should(
        "be.visible"
      )

      cy.reload()

      cy.getByTestId("UpdateWorkspaceForm.BeaconConsent").should("be.visible").should("have.class", "ant-switch-checked")

    })
  })

  describe("delete a workspace", () => {
    it("with readonly permissions", () => {
      cy.login(readonly.email, readonly.password, secondaryWorkspace.id)
        .then(() =>
          cy.visit(`/${secondaryWorkspace.slug}/settings`))

      cy.formIsDisabled("DeleteWorkspace")
    })

    it("with basic permissions", () => {
      cy.login(member.email, member.password, secondaryWorkspace.id)
        .then(() =>
          cy.visit(`/${secondaryWorkspace.slug}/settings`))

      cy.formIsDisabled("DeleteWorkspace")
    })

    it("requires the correct confirmation prompt", () => {
      cy.login(owner.email, owner.password, secondaryWorkspace.id)
        .then(() =>
          cy.visit(`/${secondaryWorkspace.slug}/settings`))

      cy.getByTestId("DeleteWorkspace.Open").click()

      cy.fillInputs({
        "DeleteWorkspace.ConfirmationPrompt": "incorrect"
      })

      cy.getByTestId("DeleteWorkspace.Submit").should("be.disabled")
    })

    it("with owner permissions", () => {
      cy.login(owner.email, owner.password, secondaryWorkspace.id)
        .then(() =>
          cy.visit(`/${secondaryWorkspace.slug}/settings`))

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
        .and("not.contain", secondaryWorkspace.name)
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, primaryWorkspace.id)
        .then(() =>
          cy.visit("/does-not-exist/settings"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login(outsider.email, outsider.password)
        .then(() =>
          cy.visit(`/${primaryWorkspace.slug}/settings`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
