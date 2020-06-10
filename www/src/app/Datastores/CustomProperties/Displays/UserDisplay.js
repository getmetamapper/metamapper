import React from "react"

const UserDisplay = ({ value }) => (
  <span>{value && value.hasOwnProperty("name") ? value.name : ""}</span>
)

export default UserDisplay
