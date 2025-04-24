import { useNavigate } from "@tanstack/react-router";

const PageNotFound404 = () => {
  const navigate = useNavigate();
  return (
    <div>
      <h1>404</h1>
      <p>Page not found</p>
      <button onClick={() => navigate({ to: "/" })}> Go Home</button>
    </div>
  );
};

export default PageNotFound404;
