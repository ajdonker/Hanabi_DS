import Card from "./Card";
import type { FlyingCard } from "./../types";


export default function FlyingCard(flyingCard: FlyingCard) {

  return (
    flyingCard && (
        <div
          className={`flying-own-card ${
            flyingCard.state === "fading" ? "is-fading" : ""
          }`.trim()}
          style={{
            left: flyingCard.fromRect.left,
            top: flyingCard.fromRect.top,
            width: flyingCard.fromRect.width,
            height: flyingCard.fromRect.height,
            transform:
              flyingCard.state === "moving" || flyingCard.state === "fading"
                ? `translate(${flyingCard.toRect.left - flyingCard.fromRect.left}px, ${
                    flyingCard.toRect.top - flyingCard.fromRect.top
                  }px) rotate(${flyingCard.rotationDeg ?? 0}deg)`
                : "translate(0px, 0px)",
          }}
        >
          <Card color={flyingCard.color} value={flyingCard.value} rotationDeg={180} numberRotationDeg={180} />
        </div>
      )
  );
}
