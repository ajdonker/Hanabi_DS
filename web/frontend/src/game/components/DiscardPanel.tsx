import type { CardColor, CardValue, DiscardTableData } from "../types";
import { colors } from "../config";

type DiscardPanelProps = {
  discardByColor: DiscardTableData;
  className?: string;
};

export default function DiscardPanel({
  discardByColor,
  className = "",
}: DiscardPanelProps) {
  const values: CardValue[] = [1, 2, 3, 4, 5];

  return (
    <aside className={`discard-panel ${className}`.trim()}>
      <table className="discard-grid">
        <thead>
          <tr>
            <th></th>
            {values.map((value) => (
              <th key={value}>{value}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {colors.map((color) => (
            <tr key={color}>
              <td className="discard-color">
                <div
                  className={`discard-color-swatch ${color.toLowerCase()}`.trim()}
                  title={color}
                />
              </td>
              {values.map((value) => (
                <td key={value}>{discardByColor[color][value]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </aside>
  );
}
