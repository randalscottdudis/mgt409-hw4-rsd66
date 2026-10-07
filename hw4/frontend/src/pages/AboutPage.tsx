export function AboutPage() {
  return (
    <main className="page about-layout">
      <div className="about-copy">
        <p className="eyebrow">About Us</p>
        <h1>Yale pride, with a little bulldog personality</h1>
        <p>
          Campus days. Game days. Wherever life takes you next. Campus Customs brings Yale spirit to your everyday
          wardrobe through Yale Bulldog Blue, our shop at 57 Broadway in New Haven.
        </p>
        <p>
          Explore hoodies, crewnecks, and tees celebrating Yale’s colleges, schools, and teams. Whether you’re finding
          a new favorite or a gift for a fellow Bulldog, there’s plenty to sniff out.
        </p>
        <p>
          Need a hand—or a paw? Ask Dan, our Handsome Dan-inspired shopping assistant, can help you discover products,
          check prices and size availability, and find in-stock alternatives. He’ll remember your conversations when
          you’re signed in, so you can pick up where you left off.
        </p>
        <p className="about-close">Find your fit. Wear your Yale pride.</p>
      </div>
      <figure className="about-photo">
        <div className="about-frame" aria-hidden="true" />
        <img
          src="/dan-3.jpg"
          alt="Illustrated Handsome Dan in sunglasses and a navy Yale jacket, holding a Yale pennant."
        />
        <GoldPaw className="about-paw about-paw-one" />
        <GoldPaw className="about-paw about-paw-two" />
      </figure>
    </main>
  )
}

function GoldPaw({ className }: { className: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" aria-hidden="true">
      <ellipse cx="32" cy="42" rx="12" ry="10" fill="#b0893e" />
      <ellipse cx="14" cy="24" rx="6" ry="8" fill="#b0893e" />
      <ellipse cx="26" cy="16" rx="6" ry="8" fill="#b0893e" />
      <ellipse cx="40" cy="16" rx="6" ry="8" fill="#b0893e" />
      <ellipse cx="52" cy="24" rx="6" ry="8" fill="#b0893e" />
    </svg>
  )
}
