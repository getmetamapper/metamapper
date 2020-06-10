import Storage from "store2"

export class UserConfiguration {
  constructor(user) {
    this.user = user
    this.email = user.email
    this.storage = Storage.namespace(this.email)
  }

  getCurrentWorkspace() {
    return this.storage.get("currentWorkspace")
  }

  setCurrentWorkspace(workspace) {
    this.storage.set("currentWorkspace", workspace)
    return workspace
  }

  removeCurrentWorkspace() {
    this.storage.remove("currentWorkspace")
    return null
  }
}

export default UserConfiguration
