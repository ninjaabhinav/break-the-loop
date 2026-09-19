import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div>
      <div className="page-header">
        <div className="eyebrow">Profile</div>
        <h1>Account</h1>
      </div>

      <div className="card form-narrow">
        <div className="field">
          <label>Name</label>
          <p>{user?.name}</p>
        </div>
        <div className="field">
          <label>Email</label>
          <p>{user?.email}</p>
        </div>
        <button className="btn btn-secondary" onClick={handleLogout}>
          Sign out
        </button>
      </div>
    </div>
  );
}
