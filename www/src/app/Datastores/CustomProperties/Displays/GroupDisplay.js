import React, { Fragment } from "react"
import GroupProfilePopover from "app/Groups/GroupProfilePopover"

const GroupDisplay = ({ value }) => (
    <Fragment>
        {value && value.hasOwnProperty("name") && (
            <GroupProfilePopover groupId={value.id}>
                {value.name}
            </GroupProfilePopover>
        )}
    </Fragment>
)

export default GroupDisplay
