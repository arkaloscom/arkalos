import { useState } from 'react'
import { BsSend } from 'react-icons/bs'

import ChatMessage from '@/components/ChatMessage'
import Api from '@/services/Api'

export default function ChatContainer({ intro }) {
  let nextId = 0

  const [STATE, SET_STATE] = useState([{ id: nextId++, data: intro, type: 'bot', is_error: false, is_loading: false }])

  function renderItems() {
    return STATE.map(renderItem)
  }

  function renderItem(item) {
    return (
      <ChatMessage
        key={item.id}
        id={item.id}
        data={item.data}
        type={item.type}
        is_error={item.is_error}
        is_loading={item.is_loading}
      />
    )
  }

  function addItem(id, message, type, is_error, is_loading) {
    SET_STATE(prevState => {
      const clone = structuredClone(prevState)
      clone.push({ id: id, data: message, type: type, is_error: is_error, is_loading: is_loading })
      return clone
    })
  }

  function updateItem(id, message, type, is_error, is_loading) {
    SET_STATE(prevState => {
      const clone = structuredClone(prevState)
      for (let i = clone.length - 1; i >= 0; i--) {
        const item = clone[i]
        if (item.id == id) {
          item.data = message
          item.type = type
          item.is_error = is_error
          item.is_loading = is_loading
          break
        }
      }
      return clone
    })
  }

  async function submitAddItem(form) {
    if (!form.checkValidity()) {
      form.reportValidity()
      return
    }
    const btn = form.querySelector('button[type="submit"]')
    if (btn.disabled) {
      return
    }
    btn.disabled = true

    const form_data = new FormData(form)

    addItem(nextId++, form.message.value, 'user', false, false)
    form.reset()
    const nextItemId = nextId
    addItem(nextId++, 'Thinking...', 'bot', false, true)

    const [data, error] = await Api.post('/chat', form_data)

    if (error) {
      updateItem(nextItemId, error.message, 'bot', true, false)
    } else if (data.response) {
      updateItem(nextItemId, data.response, 'bot', false, false)
    }

    btn.disabled = false
  }

  async function handleSubmit(event) {
    event.preventDefault()
    await submitAddItem(event.target)
  }

  async function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      await submitAddItem(event.target.form)
    }
  }

  function renderTextarea() {
    return (
      <div className="message-input-container">
        <form className="message-input-wrapper" onSubmit={handleSubmit}>
          <textarea
            name="message"
            id="message-input"
            required
            placeholder="Message Arkalos AI..."
            rows={3}
            onKeyDown={handleKeydown}
          ></textarea>
          <div className="input-controls">
            <button title="Submit message" type="submit" className="send-button" id="send-button">
              <BsSend />
            </button>
          </div>
        </form>
      </div>
    )
  }

  return (
    <div className="chat-container">
      <div className="messages-container" id="messages">
        {renderItems()}
      </div>
      {renderTextarea()}
    </div>
  )
}
