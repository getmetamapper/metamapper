// ***********************************************
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
import { queryAsString as authQuery } from "../../src/graphql/mutations/AuthenticateUser"
import { queryAsString as privilegeQuery } from "../../src/graphql/mutations/UpdateDatastoreAccessPrivileges"
import { AUTH_TOKEN, WORKSPACE_TOKEN, DEFAULT_WORKSPACE_ID } from "../../src/lib/constants"

Cypress.Commands.add("login", (email, password = "password1234", workspaceId = null) => {
  cy.request({
    url: "/graphql",
    method: "POST",
    body: {
      query: authQuery,
      variables: { email, password },
    }
  }).then((resp) => {
    if (workspaceId) {
      window.localStorage.setItem(WORKSPACE_TOKEN, workspaceId)
    }

    window.localStorage.setItem(AUTH_TOKEN, resp.body.data.tokenAuth.token)
  })
});

Cypress.Commands.add("logout", () => cy.visit("/logout"));

Cypress.Commands.add("getByTestId", element => cy.get('[data-test="' + element + '"]'));

Cypress.Commands.add("fillInputs", (elements, { wait = 0, force = true } = {}) => {
  Cypress._.map(elements, (value, testId) => {
    if (value === "" || value === null) {
      cy.getByTestId(testId).clear()
    } else {
      cy.getByTestId(testId).then(($el) => {
        if ($el.hasClass('ant-select-selection')) {
          cy.get($el)
            .click()
            .then(() => cy.get("li").contains(value).click());
        } else {
          cy.get($el).filter(":visible").clear({ force }).type(value);
        }
      })
    }
    if (wait > 0) {
      cy.wait(wait); // eslint-disable-line cypress/no-unnecessary-waiting
    }
  });
});

Cypress.Commands.add("formHasError", (element, message) => {
  cy.get(`.has-error [data-test="${element}"`).should("be.visible")
  cy.contains(".ant-form-explain", message).should(
    "be.visible"
  )
});

Cypress.Commands.add("verifyFormErrors", (formName, inputFixture) => {
  for (let [field, attributes] of Object.entries(inputFixture)) {
    if (attributes["error"] === null) {
      continue
    }

    cy.formHasError(`${formName}.${field}`, attributes["error"])
  }
});

Cypress.Commands.add("formIsDisabled", (element, onlyInclude = []) => {
  cy.get('[data-test^="' + element + '."]').each(($el, index, list) => {
    if (onlyInclude.indexOf($el.data("test")) > -1) {
      cy.get($el).should("be.disabled")
    }
  })
});
