import { useEffect, useRef } from 'react'
import embed from 'vega-embed'

export default function Chart({ spec }) {
  const chartRef = useRef()

  useEffect(() => {
    if (spec && chartRef.current) {
      const editedSpec = structuredClone(spec)
      editedSpec.background = null
      editedSpec.width = 'container'
      editedSpec.height = 'container'
      editedSpec.autosize = { type: 'fit', contains: 'padding' }

      // Set color scheme
      // Available options: https://vega.github.io/vega/docs/schemes/
      if (editedSpec.encoding?.color) {
        editedSpec.encoding.color.scale = {
          scheme: 'tableau20',
        }
      }
      embed(chartRef.current, editedSpec, {
        actions: false,
        theme: 'dark',
      })
    }
  }, [spec])

  return <b-chart ref={chartRef} />
}
