import { LIBRARY_SEED } from "@/lib/ops-data";

export default function LibraryPage() {
  const items = [...LIBRARY_SEED].sort(
    (a, b) => Number(!!b.pinned) - Number(!!a.pinned),
  );

  return (
    <div>
      <h1
        style={{
          margin: "0 0 8px",
          fontFamily: "var(--f-display)",
          fontStyle: "italic",
          fontSize: 28,
        }}
      >
        Library
      </h1>
      <p className="lede">
        Studio, Logistics, Board, and the rest of the crew toolkit — surfaced
        from the hub seed. External links open in a new tab; nothing posts from
        here.
      </p>
      <div className="lib-grid" data-testid="library-grid">
        {items.map((item) => {
          const external = item.url.startsWith("http");
          const href = item.url;
          return (
            <a
              key={item.id}
              className="lib-card"
              href={href}
              target={external ? "_blank" : undefined}
              rel={external ? "noreferrer" : undefined}
            >
              <span className="src">
                {item.source} · {item.type}
                {item.pinned ? " · pinned" : ""}
              </span>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <span className="go">{external ? "Open →" : "In panel →"}</span>
            </a>
          );
        })}
      </div>
    </div>
  );
}
