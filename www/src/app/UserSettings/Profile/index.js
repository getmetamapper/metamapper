import React from "react"
import UpdateUserProfile from "./UpdateUserProfile"

const Profile = ({ currentUser }) => (
  <div className="user-settings-profile">
    <div className="update-profile-metadata">
      <h4>Update Profile Information</h4>
      <UpdateUserProfile user={currentUser} />
    </div>
  </div>
)

export default Profile
