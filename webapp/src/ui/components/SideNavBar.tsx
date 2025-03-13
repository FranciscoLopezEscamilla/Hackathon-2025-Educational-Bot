import { Link } from "@tanstack/react-router";

const linkStyle =
  "hover:text-gray-100 hover:bg-zinc-800 rounded-sm flex p-4 border-1 border-transparent hover:border-zinc-700 transition";

const SideNavBar = () => {
  return (
    <nav className=" text-gray-400 max-w-400">
      <div className="pt-2 pb-10 px-4">
        <h1 className="font-bold text-4xl md:text-wrap 2xl:text-nowrap text-gray-100">
          AI-SSISTANT.
        </h1>
      </div>
      <ul className="text-lg font-semibold flex flex-col w-full">
        <li>
          <Link to="/" className={linkStyle}>
            Chat Assistant
          </Link>
        </li>
        <li>
          <Link to="/about" className={linkStyle}>
            History
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default SideNavBar;
