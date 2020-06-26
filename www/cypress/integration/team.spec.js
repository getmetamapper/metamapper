
describe("team.spec.js", () => {

  const workspace = {
    id: "9ae42db2-d205-463f-b5a3-61b77a0b1df7",
    name: "Santa Barbara Police Department",
    slug: "sbpd",
  }

  const otherWorkspace = {
    id: "b934d2a8-3fc9-46b8-9918-f97d5dc61fcf",
    name: "Psych",
    slug: "psych",
  }

  const owner = {
    fname: "Burton",
    lname: "Guster",
    email: "owner.team@metamapper.test",
    password: "password1234",
  }

  const otherOwner = {
    fname: "Bruton",
    lname: "Gaster",
    email: "other.owner.team@metamapper.test",
    password: "password1234",
  }

  const member = {
    fname: "John",
    lname: "Slade",
    email: "member.team@metamapper.test",
    password: "password1234",
  }

  const otherMember = {
    fname: "Hummingbird",
    lname: "Saltalamacchia",
    email: "other.member.team@metamapper.test",
    password: "password1234",
  }

  const readonly = {
    fname: "Methuselah",
    lname: "Honeysuckle",
    email: "readonly.team@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    fname: "Lavender",
    lname: "Gooms",
    email: "outsider.team@metamapper.test",
    password: "password1234",
  }

  const doesNotHavePermission = [
    { permission: "member", user: member },
    { permission: "readonly", user: readonly },
  ]

  describe("user list", () => {
    it("displays the list of users", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

      cy.title().should("eq", `Users - ${workspace.slug} - Metamapper`)

      cy.getByTestId("WorkspaceUsersTable")
        .should("exist")
        .and("contain", owner.email)
        .and("contain", member.email)
        .and("contain", readonly.email)
        .and("contain", otherMember.email)
    })
  })

  describe("invite user", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      it(`fails with ${permission} permission`, () => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/users`))

        cy.formIsDisabled("InviteUserToTeamForm", [
          "Email",
          "Submit",
        ])
      })
    })

    it("fails with an invalid email", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

      cy.fillInputs({
        "InviteUserToTeamForm.Email": "gus.tt.showbiz",
      })

      cy.getByTestId("InviteUserToTeamForm.Submit").click()

      cy.contains(
        ".ant-message-error", "The provided email address is improperly formatted."
      ).should(
        "be.visible"
      )
    })

    it("submits with default permissions", () => {
      const validEmail = "control.alt.delete@psych.ca"

      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

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
    doesNotHavePermission.forEach(({ permission, user }) => {
      it(`fails without ${permission} permission`, () => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/users`))

        cy.contains(
          "These settings can only be edited by users with the administrator role."
        ).should(
          "be.visible"
        )

        cy.get(`tr[data-row-key="${owner.email}"]`).within(() => {
          cy.get("td").eq(1).find(".ant-tag").should("not.have.class", "editable")
          cy.get("td").eq(1).find(".ant-tag").click()
          cy.get("td").eq(1).find(".ant-select-selection-selected-value").should("not.be.visible")
        })

        cy.getByTestId("WorkspaceUsersTable").should("exist").and("contain", owner.email)
      })
    })

    it("cannot update yourself", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

      cy.get(`tr[data-row-key="${owner.email}"]`).within(() => {
        cy.get("td").eq(1).find(".ant-tag").should("have.class", "editable")
        cy.get("td").eq(1).find(".ant-tag").click()
        cy.get("td").eq(1).find(".ant-select-selection-selected-value").click()
      })

      cy.get(".ant-select-dropdown-menu-item").contains("Member").click()
      cy.get(".update-user-permissions").find(".ant-btn-primary").click()

      cy.contains(".ant-message-error", "You cannot alter your own membership.").should(
        "be.visible"
      )

      cy.getByTestId("WorkspaceUsersTable").should("exist").and("contain", owner.email)
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
      let targetEmail = `${user.from.toLowerCase()}.team@metamapper.test`

      it(`can update from ${user.from} to ${user.to}`, () => {
        cy.login(otherOwner.email, otherOwner.password, otherWorkspace.id)
          .then(() =>
            cy.visit(`/${otherWorkspace.slug}/settings/users`))

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
    const emailToRemove = otherMember.email

    doesNotHavePermission.forEach(({ permission, user }) => {
      it(`fails without ${permission} permission`, () => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/users`))

        cy.get(`tr[data-row-key="${emailToRemove}"]`).within(() => {
          cy.get("td").eq(0).contains(emailToRemove)
          cy.get("td").eq(2).contains("Remove").should("be.disabled")
        })
      })
    })

    it("using UI", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

      cy.get(`tr[data-row-key="${emailToRemove}"]`).within(() => {
        cy.get("td").eq(0).contains(emailToRemove)
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
        .and("not.contain", emailToRemove)
    })

    it("cannot remove yourself as last owner", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

      cy.get(`tr[data-row-key="${owner.email}"]`).within(() => {
        cy.get("td").eq(0).contains(owner.email)
        cy.get("td").eq(2).contains("Leave").should("be.disabled")
      })
    })

    it("removing yourself as regular user", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

      cy.get(`tr[data-row-key="${member.email}"]`).within(() => {
        cy.get("td").eq(0).contains(member.email)
        cy.get("td").eq(2).contains("Leave").should("not.be.disabled")
        cy.get("td").eq(2).contains("Leave").trigger("mouseover")
        cy.get("td").eq(2).contains("Leave").click()
      })

      cy.contains("Yes").click()

      cy.location("pathname").should("equal", "/workspaces")

      cy.getByTestId("WorkspaceList")
        .should("exist")
        .and("not.contain", workspace.name)
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, otherWorkspace.id)
        .then(() =>
          cy.visit("/does-not-exist/settings/users"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login(outsider.email, outsider.password, otherWorkspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/users`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
