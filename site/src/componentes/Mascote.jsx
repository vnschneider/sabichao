import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "motion/react";

export default function Mascote({ comemorando }) {
  const reduzir = useReducedMotion();
  const [pose, setPose] = useState("acenando");

  useEffect(() => {
    if (reduzir) {
      setPose("normal");
      return;
    }
    const tempos = [];
    tempos.push(setTimeout(() => setPose("normal"), 2600));
    const piscar = setInterval(() => {
      setPose((atual) => (atual === "normal" ? "piscando" : atual));
      tempos.push(setTimeout(() => setPose((atual) => (atual === "piscando" ? "normal" : atual)), 170));
    }, 3800);
    return () => {
      tempos.forEach(clearTimeout);
      clearInterval(piscar);
    };
  }, [reduzir]);

  const visivel = comemorando ? "comemorando" : pose;

  return (
    <motion.div
      className="mascote"
      initial={reduzir ? false : { opacity: 0, scale: 0.9, rotate: -4 }}
      animate={{ opacity: 1, scale: 1, rotate: 0 }}
      transition={{ type: "spring", stiffness: 120, damping: 14, delay: 0.1 }}
    >
      <motion.div
        className="mascote-corpo"
        animate={reduzir ? undefined : { y: comemorando ? [0, -18, 0] : [0, -6, 0] }}
        transition={
          comemorando
            ? { duration: 0.45, repeat: 2, ease: "easeOut" }
            : { duration: 3.4, repeat: Infinity, ease: "easeInOut" }
        }
      >
        {["acenando", "normal", "piscando", "comemorando"].map((p) => (
          <img
            key={p}
            src={`/mascote-${p}.svg`}
            alt={p === "acenando" ? "Mascote do Sabichao, uma coruja com capelo, acenando" : ""}
            aria-hidden={p !== "acenando"}
            width="340"
            height="320"
            className={p === visivel ? "ativa" : ""}
            fetchPriority={p === "acenando" ? "high" : "low"}
          />
        ))}
      </motion.div>
      <div className="mascote-sombra" aria-hidden="true" />
    </motion.div>
  );
}
