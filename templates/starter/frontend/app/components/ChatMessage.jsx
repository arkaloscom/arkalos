import ErrorMessage from './ErrorMessage'
import LoadingIndicator from './LoadingIndicator'
import Markdown from './Markdown'

export default function ChatMessage({ id, data, type, is_error, is_loading }) {
  function renderUserAvatar() {
    return <div className="avatar-placeholder" />
  }

  function renderBotAvatar() {
    return (
      <div className="bot-avatar">
        <img src="https://arkalos.com/assets/img/arkalos-logo.png" alt="Arkalos Logo" className="avatar-logo" />
      </div>
    )
  }

  function renderAvatar() {
    if (type === 'bot') {
      return renderBotAvatar()
    }
    return renderUserAvatar()
  }

  function renderUserMessage() {
    return <div className="message user">{data && data}</div>
  }

  function renderBotMessage() {
    if (is_error) {
      return <ErrorMessage className="message bot error" message={data} />
    }
    if (is_loading) {
      return <LoadingIndicator className="message bot typing-indicator" text="Thinking" />
    }
    return (
      <div className="message bot">
        <Markdown>{data}</Markdown>
      </div>
    )
  }

  function renderMessage() {
    if (type === 'bot') {
      return renderBotMessage()
    }
    return renderUserMessage()
  }

  return (
    <div className="message-row" data-id={id}>
      {renderAvatar()}
      {renderMessage()}
    </div>
  )
}
