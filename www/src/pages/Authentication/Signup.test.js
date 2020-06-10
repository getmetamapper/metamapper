import React from "react"
import { render } from "test/utils"
import clientMock from "test/client-mock"

import Signup from "./Signup"

describe("Signup", () => {
  it("renders", () => {
    expect(render(clientMock, Signup).find("AuthForm").length).toEqual(1)
  })
})
