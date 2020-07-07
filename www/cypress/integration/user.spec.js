
const openUserSettingsPanel = (pageName = "Profile") =>{
  cy.getByTestId("Navbar.Dropdown").click()
  cy.contains("User Settings").click()
  cy.contains(pageName).click()
}

describe("user.spec.js", () => {
  // Fixtures...
  const workspace = {
    id: "5bd01b7f-9dd0-42e7-b265-3dea81c89a84",
    name: "Los Pollos Hermanos",
    slug: "los-pollos-hermanos",
  }

  const currentUser = {
    fname: "Walter",
    lname: "White",
    email: "current.user@metamapper.test",
    password: "password1234",
  }

  const newProperties = {
    fname: "Werner",
    lname: "Heisenberg",
    email: "heisenberg@metamapper.test",
  }

  const passwords = {
    incorrect: "password54321",
    current: "password1234",
    newSafe: "Ccbc;gNr$-L+6@Z]",
    newWeak: "banana",
  }

  const anotherUser = {
    fname: "Gus",
    lname: "Fring",
    email: "another.user@metamapper.test",
  }

  describe("edit user profile", () => {
    beforeEach(() => {
      cy.login(currentUser.email).then(() => cy.visit(`/${workspace.slug}/datastores`))

      openUserSettingsPanel("Profile")
    })

    it("requires a password", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": newProperties.fname,
        "UpdateUserProfileForm.LastName": newProperties.lname,
        "UpdateUserProfileForm.Email": currentUser.email,
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.formHasError("UpdateUserProfileForm.CurrentPassword", "This field is required.")
    })

    it("requires a correct password", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": newProperties.fname,
        "UpdateUserProfileForm.LastName": newProperties.lname,
        "UpdateUserProfileForm.Email": currentUser.email,
        "UpdateUserProfileForm.CurrentPassword": "bananas",
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-error", "The password you provided is incorrect.").should(
        "be.visible"
      )
    })

    const formValidationFixtures = [
      {
        describe: "validates required fields",
        inputs: {
          "Email": { value: "", error: "This field is required." },
          "FirstName": { value: "", error: "This field is required." },
          "LastName": { value: "", error: "This field is required." },
        },
      },
      {
        describe: "validates email format",
        inputs: {
          "Email": { value: "guster.com", error: "Email format is invalid." },
          "FirstName": { value: "Burton", error: null },
          "LastName": { value: "Guster", error: null },
        },
      },
      {
        describe: "validate name length",
        inputs: {
          "Email": { value: currentUser.email, error: null },
          "FirstName": {
            value: (Math.random()*1e256).toString(36),
            error: "This field must be less than 60 characters.",
          },
          "LastName": {
            value: (Math.random()*1e256).toString(36),
            error: "This field must be less than 60 characters.",
          },
        },
      },
    ]

    formValidationFixtures.forEach(({ describe, inputs }) => {
      it(describe, () => {
        cy.fillInputs({
          "UpdateUserProfileForm.FirstName": inputs["FirstName"]["value"],
          "UpdateUserProfileForm.LastName": inputs["LastName"]["value"],
          "UpdateUserProfileForm.Email": inputs["Email"]["value"],
          "UpdateUserProfileForm.CurrentPassword": currentUser.password,
        })

        cy.getByTestId("UpdateUserProfileForm.Submit").click()

        cy.verifyFormErrors("UpdateUserProfileForm", inputs)
      })
    })

    it("requires a unique email address", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": newProperties.fname,
        "UpdateUserProfileForm.LastName": newProperties.lname,
        "UpdateUserProfileForm.Email": anotherUser.email,
        "UpdateUserProfileForm.CurrentPassword": currentUser.password,
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-error", "User with this email already exists.").should(
        "be.visible"
      )

      cy.reload()

      openUserSettingsPanel("Profile")

      cy.getByTestId("UpdateUserProfileForm.FirstName").should(
        "not.have.value",
        newProperties.fname,
      )

      cy.getByTestId("UpdateUserProfileForm.LastName").should(
        "not.have.value",
        newProperties.lname,
      )

      cy.getByTestId("UpdateUserProfileForm.Email").should(
        "not.have.value",
        anotherUser.email,
      )
    })

    it("using UI", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": newProperties.fname,
        "UpdateUserProfileForm.LastName": newProperties.lname,
        "UpdateUserProfileForm.Email": newProperties.email,
        "UpdateUserProfileForm.CurrentPassword": currentUser.password,
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Your profile has been updated.").should(
        "be.visible"
      )

      cy.reload()

      openUserSettingsPanel("Profile")

      cy.getByTestId("UpdateUserProfileForm.FirstName").should(
        "have.value",
        newProperties.fname,
      )

      cy.getByTestId("UpdateUserProfileForm.LastName").should(
        "have.value",
        newProperties.lname,
      )

      cy.getByTestId("UpdateUserProfileForm.Email").should(
        "have.value",
        newProperties.email,
      )
    })
  })

  describe("edit user password", () => {
    beforeEach(() => {
      cy.login(newProperties.email).then(() => cy.visit(`/${workspace.slug}`))

      openUserSettingsPanel("Security")
    })

    it("requires the correct current password", () => {
      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.incorrect,
        "UpdatePasswordForm.NewPassword": passwords.newSafe,
        "UpdatePasswordForm.ConfirmPassword": passwords.newSafe,
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()
      cy.getByTestId("UpdatePasswordForm.Submit").should("be.disabled")

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-error", "The password you provided is incorrect.").should(
        "be.visible"
      )
    })

    it("requires the password and the confirmation to match", () => {
      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.current,
        "UpdatePasswordForm.NewPassword": passwords.newSafe,
        "UpdatePasswordForm.ConfirmPassword": passwords.newSafe + "x",
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()

      cy.formHasError("UpdatePasswordForm.ConfirmPassword", "Confirmation must match new password.")
    })

    it("requires a strong password", () => {
      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.current,
        "UpdatePasswordForm.NewPassword": passwords.newWeak,
        "UpdatePasswordForm.ConfirmPassword": passwords.newWeak,
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()

      cy.formHasError("UpdatePasswordForm.NewPassword", "Password is not strong enough.")
    })

    it("using UI", () => {
      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.current,
        "UpdatePasswordForm.NewPassword": passwords.newSafe,
        "UpdatePasswordForm.ConfirmPassword": passwords.newSafe,
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()
      cy.getByTestId("UpdatePasswordForm.Submit").should("be.disabled")

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Your password has been changed.").should(
        "be.visible"
      )

      // It should clear the form.
      cy.getByTestId("UpdatePasswordForm.CurrentPassword").should("have.value", "")
      cy.getByTestId("UpdatePasswordForm.NewPassword").should("have.value", "")
      cy.getByTestId("UpdatePasswordForm.ConfirmPassword").should("have.value", "")

      // It should keep the user logged in.
      cy.reload()

      cy.location("pathname").should("equal", `/${workspace.slug}/datastores`)

      // It should allow the user to log in with the new password.
      cy.logout()

      cy.location("pathname").should("equal", "/login")

      cy.getByTestId("LoginPromptForm.Email").type(newProperties.email)
      cy.contains("button", "Continue with Email").click()

      cy.getByTestId("LoginForm.Password").type(passwords.newSafe)
      cy.contains("button", "Sign In").click()

      cy.contains("The search engine for your data.").should("be.visible")
    })
  })
})
