import React, { Fragment } from "react"
import UserProfilePopover from "app/Users/UserProfilePopover"

const UserDisplay = ({ value }) => (
    <Fragment>
        {value && value.hasOwnProperty("name") && (
            <UserProfilePopover userId={value.id}>
                {value.name}
            </UserProfilePopover>
        )}
    </Fragment>
)

export default UserDisplay
