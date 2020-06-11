import { DEFAULT_WORKSPACE_ID, DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("team.spec.js", () => {
  afterEach(() => {
    cy.logout()
  })

  let doesNotHavePermission = ["readonly", "member"]

  describe("user list", () => {
    it("displays the list of users", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

      cy.title().should("eq", "Users - dunder-mifflin - Metamapper")

      cy.getByTestId("WorkspaceUsersTable")
        .should("exist")
        .and("contain", "owner@metamapper.io")
        .and("contain", "member@metamapper.io")
        .and("contain", "readonly@metamapper.io")
    })
  })

  describe("invite user", () => {
    doesNotHavePermission.forEach((permission) => {
      it(`fails with ${permission} permission`, () => {
        cy.quickLogin(permission)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

        cy.formIsDisabled("InviteUserToTeamForm", [
            "Email",
            "Submit",
        ])
      })
    })

    it("fails with an invalid email", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

      let invalidEmail = "henry.spencer"

      cy.fillInputs({
        "InviteUserToTeamForm.Email": invalidEmail,
      })

      cy.getByTestId("InviteUserToTeamForm.Submit").click()

      cy.contains(
        ".ant-message-error", "The provided email address is improperly formatted."
      ).should(
        "be.visible"
      )
    })

    it("submits with default permissions", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

      let validEmail = "henry.spencer@psych.ca"

      cy.fillInputs({
        "InviteUserToTeamForm.Email": validEmail,
      })

      cy.getByTestId("InviteUserToTeamForm.Submit").click()

      cy.contains(
        ".ant-message-success", "User has been invited."
      ).should(
        "be.visible"
      )

      cy.reload()

      cy.get(`tr[data-row-key="${validEmail}"]`).within(() => {
        cy.get("td").eq(0).contains(validEmail)
        cy.get("td").eq(1).contains("Member")
      })
    })
  })

  describe("update permissions", () => {
    let targetEmail = "owner@metamapper.io"

    doesNotHavePermission.forEach((permission) => {
      it(`fails without ${permission} permission`, () => {
        cy.login(`${permission}@metamapper.io`, "password1234", DEFAULT_WORKSPACE_ID)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

        cy.contains(
          "These settings can only be edited by users with the administrator role."
        ).should(
          "be.visible"
        )

        cy.get(`tr[data-row-key="${targetEmail}"]`).within(() => {
          cy.get("td").eq(1).find(".ant-tag").should("not.have.class", "editable")
          cy.get("td").eq(1).find(".ant-tag").click()
          cy.get("td").eq(1).find(".ant-select-selection-selected-value").should("not.be.visible")
        })

        cy.getByTestId("WorkspaceUsersTable").should("exist").and("contain", targetEmail)
      })
    })

    it("cannot update yourself", () => {
      let yourself = "owner@metamapper.io"

      cy.login(yourself, "password1234", DEFAULT_WORKSPACE_ID)
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

      cy.get(`tr[data-row-key="${yourself}"]`).within(() => {
        cy.get("td").eq(1).find(".ant-tag").should("have.class", "editable")
        cy.get("td").eq(1).find(".ant-tag").click()
        cy.get("td").eq(1).find(".ant-select-selection-selected-value").click()
      })

      cy.get(".ant-select-dropdown-menu-item").contains("Member").click()
      cy.get(".update-user-permissions").find(".ant-btn-primary").click()

      cy.contains(".ant-message-error", "You cannot alter your own membership.").should(
        "be.visible"
      )

      cy.getByTestId("WorkspaceUsersTable").should("exist").and("contain", yourself)
    })

    let userFixtures = [
      {from: "Readonly", to: "Member"},
      {from: "Readonly", to: "Owner"},
      {from: "Readonly", to: "Readonly"},
      {from: "Member", to: "Readonly"},
      {from: "Member", to: "Owner"},
      {from: "Member", to: "Member"},
      {from: "Owner", to: "Readonly"},
      {from: "Owner", to: "Member"},
      {from: "Owner", to: "Owner"},
    ]

    userFixtures.forEach((user) => {
      let targetEmail = `${user.from.toLowerCase()}@metamapper.io`

      it(`can update from ${user.from} to ${user.to}`, () => {
        let loggedInUser = "other.owner@metamapper.io"

        cy.login(loggedInUser, "password1234", DEFAULT_WORKSPACE_ID)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

        cy.get(`tr[data-row-key="${targetEmail}"]`).within(() => {
          cy.get("td").eq(1).find(".ant-tag").should("have.class", "editable")
          cy.get("td").eq(1).find(".ant-tag").click()
          cy.get("td").eq(1).find(".ant-select-selection-selected-value").click()
        })

        // Click through and update the permissions.
        cy.get(".ant-select-dropdown-menu-item").contains(user.to).click()
        cy.get(".update-user-permissions").find(".ant-btn-primary").click()

        // It displays the successful message.
        cy.contains(".ant-message-success", "Membership has been updated.").should(
          "be.visible"
        )

        // It updates the permissions on the user table.
        cy.get(`tr[data-row-key="${targetEmail}"]`).within(() => {
          cy.get("td").eq(1).contains(user.to)
        })
      })
    })
  })

  describe("remove user", () => {
    let targetEmail = "other.owner@metamapper.io"

    doesNotHavePermission.forEach((permission) => {
      it(`fails without ${permission} permission`, () => {
        cy.login(`${permission}@metamapper.io`, "password1234", DEFAULT_WORKSPACE_ID)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

        cy.get(`tr[data-row-key="${targetEmail}"]`).within(() => {
          cy.get("td").eq(0).contains(targetEmail)
          cy.get("td").eq(2).contains("Remove").should("be.disabled")
        })
      })
    })

    it("using UI", () => {
      cy.login("owner@metamapper.io", "password1234", DEFAULT_WORKSPACE_ID)
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

      cy.get(`tr[data-row-key="${targetEmail}"]`).within(() => {
        cy.get("td").eq(0).contains(targetEmail)
        cy.get("td").eq(2).contains("Remove").should("not.be.disabled")
        cy.get("td").eq(2).contains("Remove").click()
      })

      cy.contains("Yes").click()

      cy.contains(
        ".ant-message-success", "User has been removed."
      ).should(
        "be.visible"
      )

      cy.getByTestId("WorkspaceUsersTable")
        .should("exist")
        .and("not.contain", targetEmail)
    })

    it("removing yourself as last owner", () => {
      let email = "owner@metamapper.io"

      cy.login(email, "password1234", DEFAULT_WORKSPACE_ID)
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

      cy.get(`tr[data-row-key="${email}"]`).within(() => {
        cy.get("td").eq(0).contains(email)
        cy.get("td").eq(2).contains("Leave").should("be.disabled")
      })
    })

    it("removing yourself", () => {
      let email = "member@metamapper.io"

      cy.login(email, "password1234", DEFAULT_WORKSPACE_ID)
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`).wait(1000))

      cy.get(`tr[data-row-key="${email}"]`).within(() => {
        cy.get("td").eq(0).contains(email)
        cy.get("td").eq(2).contains("Leave").should("not.be.disabled")
        cy.get("td").eq(2).contains("Leave").trigger("mouseover")
        cy.get("td").eq(2).contains("Leave").click()
      })

      cy.contains("Yes").click()

      cy.location("pathname").should("equal", "/workspaces")
      cy.getByTestId("WorkspaceList")
        .should("exist")
        .and("not.contain", "Dunder Mifflin")
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit("/does-not-exist/settings/users"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/users`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
