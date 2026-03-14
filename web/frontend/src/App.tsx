import { Routes, Route, Outlet, Link } from "react-router-dom";
import Login from "./login/login";
import Lobby from "./lobby/lobby";
import Waiting from "./waiting/waiting";
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
    <Outlet />
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
