import React from "react"
import { render } from "test/utils"
import clientMock from "test/client-mock"

import Login from "./Login"

describe("Login", () => {
  it("renders", () => {
    expect(render(clientMock, Login).find("AuthForm").length).toEqual(1)
  })
})
