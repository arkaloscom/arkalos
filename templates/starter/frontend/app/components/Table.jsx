export default function Table({ data, columns }) {
  function renderHeaderRow(columns) {
    return <tr>{Object.keys(columns).map(key => renderHeaderRowCell(columns[key], key))}</tr>
  }

  function renderHeaderRowCell(column, key) {
    return <th key={key}>{column.title}</th>
  }

  function renderRows(data, columns) {
    return data.map((data_row, index) => renderRow(data_row, index, columns))
  }

  function renderRow(data_row, index, columns) {
    return (
      <tr key={index}>
        {Object.keys(columns).map(prop_key => {
          const fn = columns[prop_key]['fn'] ?? null
          const style = columns[prop_key]['style'] ?? null
          if (data_row[prop_key] === undefined) {
            return renderRowCell('Table error: data[' + prop_key + '] not found', prop_key, fn)
          }
          return renderRowCell(data_row[prop_key], prop_key, fn, data_row, style)
        })}
      </tr>
    )
  }

  function renderRowCell(content, key, fn, data_row, style) {
    return (
      <td key={key} style={style}>
        {renderCellContent(content, fn, data_row)}
      </td>
    )
  }

  function renderCellContent(content, fn, data_row) {
    if (fn) {
      return fn(content, data_row)
    }
    return content
  }

  function render() {
    return (
      <table>
        <thead>{renderHeaderRow(columns)}</thead>
        <tbody>{renderRows(data, columns)}</tbody>
      </table>
    )
  }

  return render()
}
