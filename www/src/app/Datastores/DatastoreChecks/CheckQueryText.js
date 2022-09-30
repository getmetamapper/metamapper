import React from "react"
import { Icon } from "antd"
import { copyToClipboard } from "lib/utilities"
import CodeMirrorEditor from "app/Common/CodeMirror/CodeMirrorEditor"

const CheckQueryText = ({ sqlText, hasFooter }) => (
  <div className="check-query-text">
    <CodeMirrorEditor
      mode="sql"
      theme="base16-light"
      value={sqlText}
      placeholder="read"
      readOnly={true}
      lineWrapping={true}
      lineNumbers={true}
    />
    {hasFooter && (
      <div className="check-query-text-footer">
        <div className="check-query-text-copy" onClick={() => copyToClipboard(sqlText)}>
          <Icon type="copy" /> Copy to Clipboard
        </div>
      </div>
    )}
  </div>
)

CheckQueryText.defaultProps = {
  sqlText: '',
  hasFooter: false,
}

export default CheckQueryText
