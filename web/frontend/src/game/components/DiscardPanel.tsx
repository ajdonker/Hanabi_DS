import type { CardColor, DiscardTableData } from "../types";

type DiscardPanelProps = {
  discardByColor: DiscardTableData;
  className?: string;
};

type TableRow = {
  color: CardColor;
  col2: string;
  col3: string;
  col4: string;
  col5: string;
};

function buildRow(color: CardColor, discardByColor: DiscardTableData): TableRow {
  const counts = discardByColor[color];
  const oneCount = Math.min(2, counts.ones);
  const twoCount = Math.min(2, counts.twos);
  const threeCount = Math.min(2, counts.threes);

  const col2 = oneCount >= 1 ? "1" : "";
  const col3Parts: string[] = [];
  if (oneCount >= 2) {
    col3Parts.push("1");
  }
  if (twoCount >= 1) {
    col3Parts.push("2");
  }

  const col4Parts: string[] = [];
  if (twoCount >= 2) {
    col4Parts.push("2");
  }
  if (threeCount >= 1) {
    col4Parts.push("3");
  }

  const col5 = threeCount >= 2 ? "3" : "";

  return {
    color,
    col2,
    col3: col3Parts.join(" / "),
    col4: col4Parts.join(" / "),
    col5,
  };
}

export default function DiscardPanel({
  discardByColor,
  className = "",
}: DiscardPanelProps) {
  const colors: CardColor[] = ["Green", "White", "Red", "Blue", "Yellow"];
  const rows = colors.map((color) => buildRow(color, discardByColor));

  return (
    <aside className={`discard-panel ${className}`.trim()}>
      <h3>Discard Table</h3>
      <table className="discard-grid">
        <thead>
          <tr>
            <th>Color</th>
            <th>2</th>
            <th>3</th>
            <th>4</th>
            <th>5</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.color}>
              <td className="discard-color">{row.color}</td>
              <td>{row.col2}</td>
              <td>{row.col3}</td>
              <td>{row.col4}</td>
              <td>{row.col5}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </aside>
  );
}
