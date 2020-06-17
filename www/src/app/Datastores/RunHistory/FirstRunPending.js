import React from "react"
import { Icon, Spin } from "antd"
import Link from "app/Navigation/Link"

const FirstRunPending = ({ datastore }) => (
  <div className="first-run-pending">
    <h3>
        Metamapper is scanning and indexing your datastore.
    </h3>
    <p>
        This might take a few minutes. You can monitor progress
        from the <Link to={`/datastores/${datastore.slug}/runs`}>Run History</Link> page.
    </p>
    <Spin indicator={<Icon type="loading" spin style={{ fontSize: 48 }} />} />
  </div>
)

export default FirstRunPending
