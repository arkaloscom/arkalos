import { NavLink } from 'react-router'

export default function Nav() {
  return (
    <nav>
      <b-logo>
        <NavLink to="/">
          <img src="https://arkalos.com/assets/img/arkalos-logo.png" alt="Arkalos Logo" className="header-logo" />
          {/* <div>Arkalos</div> */}
        </NavLink>
      </b-logo>
      <b-menu>
        <NavLink to="/">Home</NavLink>
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/chat">Chat</NavLink>
        <NavLink to="/logs">Logs</NavLink>
      </b-menu>
    </nav>
  )
}
