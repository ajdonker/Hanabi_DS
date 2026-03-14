import { Routes, Route, Outlet, Link } from "react-router-dom";
import Login from "./login/login";
import Lobby from "./lobby";
import Waiting from "./waiting";
import Game from "./game";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route path="login" element={<Login />} />
        <Route path="lobby" element={<Lobby />} />
        <Route path="waiting/:tableId" element={<Waiting />} />
        <Route path="game/:tableId" element={<Game />} />
        <Route path="*" element={<NoMatch />} />
      </Route>
    </Routes>
  );
}

function Layout() {
  return (
    <div>
      <h1>Hanabi</h1>
      <nav>
        <ul>
          <li>
            <Link to="/login">Login</Link>
          </li>
          <li>
            <Link to="/lobby">Lobby</Link>
          </li>
        </ul>
      </nav>
      <hr />
      <Outlet />
    </div>
  );
}

function NoMatch() {
  return (
    <div>
      <h2>Nothing to see here!</h2>
      <p>
        <Link to="/">Go to the home page</Link>
      </p>
    </div>
  );
}
