import { AUTH_TOKEN, WORKSPACE_TOKEN } from "../../src/lib/constants"

// Mimic the login prompt form process. This should redirect
// the user to `/login/email` if the email is registered, otherwise it
// will forward to the `/signup` page.
const continueWithEmail = (email) =>{
  cy.getByTestId("LoginPromptForm.Email").type(email)
  cy.contains(
    "button",
    "Continue with Email",
  ).click()
}

describe("authentication.spec.js", () => {
  // Fixtures...
  const workspace = {
    name: "Los Angeles",
    slug: "los-angeles",
  }

  const validUser = {
    fname: "Robert",
    lname: "Neville",
    email: "owner.authentication@metamapper.test",
    password: "password1234",
  }

  const unregisteredUser = {
    fname: "Ruth",
    lname: "Doe",
    email: "unregistered.authentication@metamapper.test",
  }

  const strongPassword = "}~Q9%tu$CnU6>nUE"

  const weakPassword = "password1234"

  describe("login", () => {
    beforeEach(() => {
      cy.visit("/login")
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Log In - Metamapper")
    })

    it("requires the correct password", () => {
      continueWithEmail(validUser.email)

      // fill in an INCORRECT password
      cy.getByTestId("LoginForm.Password").type("wrong-password")

      // Click to sign in...
      cy.contains("button", "Sign In").click()

      // still on /login page plus an error is displayed
      cy.location("pathname").should("equal", "/login/email")
      cy.contains(".ant-alert.ant-alert-error", "Incorrect login credentials.").should(
        "be.visible"
      )
    })

    it("redirects to sign up when email is not registered", () => {
      continueWithEmail(unregisteredUser.email)

      // confirm we get redirected to the sign up page
      cy.location("pathname").should("equal", "/signup")
      cy.contains("Create an Account").should("be.visible")

      cy.location("search").should("equal", `?email=${unregisteredUser.email}`)

      // Form should be prefilled based on the URL parameter.
      cy.getByTestId("SignupForm.Email").should("have.value", unregisteredUser.email)
    })

    it("fails to access protected resource", () => {
      cy.visit("/")
      cy.location("pathname").should("equal", "/login")
    })

    it("using UI", () => {
      continueWithEmail(validUser.email)

      // fill in the CORRECT password
      cy.getByTestId("LoginForm.Password").type(validUser.password)
      cy.contains("button", "Sign In").click()

      // confirm we have logged in successfully
      cy.location("pathname").should("equal", `/${workspace.slug}`)
        .then(() => {
          expect(
            window.localStorage.getItem(AUTH_TOKEN)
          ).to.be.a("string")
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.be.a("string")
        })
    })
  })

  describe("reset password", () => {
    beforeEach(() => {
      cy.visit("/password/reset")
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Reset Your Password - Metamapper")
    })

    it("fails if email does not exist", () => {
      cy.fillInputs({
        "PasswordResetForm.Email": unregisteredUser.email,
      })

      cy.getByTestId("PasswordResetForm.Submit").click()

      cy.location("pathname").should("equal", "/password/reset")
      cy.contains(
        ".ant-alert.ant-alert-error",
        "We aren't sure if this account exists.",
      ).should(
        "be.visible"
      )
    })

    it("using UI", () => {
      cy.fillInputs({
        "PasswordResetForm.Email": validUser.email,
      })

      cy.getByTestId("PasswordResetForm.Submit").click()

      cy.location("pathname").should("equal", "/password/reset")
      cy.contains(
        ".ant-alert.ant-alert-success",
        "We have sent an email with instructions to reset your password.",
      ).should(
        "be.visible"
      )
    })
  })

  describe("sign up", () => {
    beforeEach(() => {
      cy.visit("/signup")
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Sign Up - Metamapper")
    })

    it("fails if the user is already registered", () => {
      cy.fillInputs({
        "SignupForm.FirstName": unregisteredUser.fname,
        "SignupForm.LastName": unregisteredUser.lname,
        "SignupForm.Email": validUser.email,
        "SignupForm.Password": strongPassword,
      })

      cy.getByTestId("SignupForm.Submit").click()

      cy.location("pathname").should("equal", "/signup")
      cy.contains(".ant-alert.ant-alert-error", "User with this email already exists.").should(
        "be.visible"
      )
    })

    it("fails if the password is too weak", () => {
      cy.fillInputs({
        "SignupForm.FirstName": unregisteredUser.fname,
        "SignupForm.LastName": unregisteredUser.lname,
        "SignupForm.Email": unregisteredUser.email,
        "SignupForm.Password": weakPassword,
      })

      cy.getByTestId("SignupForm.Submit").click()

      cy.location("pathname").should("equal", "/signup")

      cy.formHasError(
        "SignupForm.Password",
        "Password is not strong enough.",
      )
    })

    it("using UI", () => {
      cy.fillInputs({
        "SignupForm.FirstName": unregisteredUser.fname,
        "SignupForm.LastName": unregisteredUser.lname,
        "SignupForm.Email": unregisteredUser.email,
        "SignupForm.Password": strongPassword,
      })

      cy.getByTestId("SignupForm.Submit").click()

      // It should redirect to the workspaces page. Eventually this should be an onboarding page.
      cy.location("pathname").should("equal", "/workspaces")
        .then(() => {
          expect(
            window.localStorage.getItem(AUTH_TOKEN)
          ).to.be.a("string")
        })
    })
  })

  describe("logout", () => {
    beforeEach(() => {
      cy.login(validUser.email).then(() => cy.visit(`/${workspace.slug}/datastores`))
    })

    it("shows login page after logout", () => {
      cy.getByTestId("Navbar.Dropdown").should("be.visible")
      cy.getByTestId("Navbar.Dropdown").click()

      cy.contains("Sign Out").click()

      cy.location("pathname").should("equal", "/login")
      cy.title().should("eq", "Log In - Metamapper")
    })
  })

  describe("automatic redirection", () => {

    it("does not redirect to cross-origin domain", () => {
      cy.visit("/login?next=https://www.google.com")

      continueWithEmail(validUser.email)

      cy.getByTestId("LoginForm.Password").type(validUser.password)
      cy.contains("button", "Sign In").click()

      cy.location("pathname").should("equal", `/${workspace.slug}`)
    })

    it("redirects to root when target is login page", () => {
      cy.visit("/login?next=" + encodeURIComponent(`${Cypress.config().baseUrl}/login`))

      continueWithEmail(validUser.email)

      cy.getByTestId("LoginForm.Password").type(validUser.password)
      cy.contains("button", "Sign In").click()

      cy.location("pathname").should("equal", `/${workspace.slug}`)
    })

    it("redirects when added automatically", () => {
      cy.visit(`/${workspace.slug}/settings/groups`)

      cy.location("pathname").should("equal", "/login")
      cy.location("search").should("equal", '?next=' + encodeURIComponent(`${Cypress.config().baseUrl}/${workspace.slug}/settings/groups`))

      continueWithEmail(validUser.email)

      cy.getByTestId("LoginForm.Password").type(validUser.password)
      cy.contains("button", "Sign In").click()

      cy.location("pathname").should("equal", `/${workspace.slug}/settings/groups`)
    })

    it("redirects when added manually", () => {
      cy.visit("/login?next=" + encodeURIComponent(`${Cypress.config().baseUrl}/${workspace.slug}/settings/groups`))

      cy.location("pathname").should("equal", "/login")
      cy.location("search").should("equal", '?next=' + encodeURIComponent(`${Cypress.config().baseUrl}/${workspace.slug}/settings/groups`))

      continueWithEmail(validUser.email)

      cy.getByTestId("LoginForm.Password").type(validUser.password)
      cy.contains("button", "Sign In").click()

      cy.location("pathname").should("equal", `/${workspace.slug}/settings/groups`)
    })

    it("redirects to 404 when page is invalid", () => {
      cy.visit("/login?next=" + encodeURIComponent(`${Cypress.config().baseUrl}/${workspace.slug}/does-not/exist`))

      continueWithEmail(validUser.email)

      cy.getByTestId("LoginForm.Password").type(validUser.password)
      cy.contains("button", "Sign In").click()

      cy.location("pathname").should("equal", `/${workspace.slug}/does-not/exist`)
      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
