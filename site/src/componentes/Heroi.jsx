import { useState } from "react";
import { motion, useReducedMotion } from "motion/react";
import Instalar from "./Instalar.jsx";
import Mascote from "./Mascote.jsx";
import "./Heroi.css";

export default function Heroi() {
  const [comemorando, setComemorando] = useState(false);
  const reduzir = useReducedMotion();

  function aoCopiar() {
    setComemorando(true);
    setTimeout(() => setComemorando(false), 2200);
  }

  const entrada = (atraso) =>
    reduzir
      ? {}
      : {
          initial: { opacity: 0, y: 18 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.7, delay: atraso, ease: [0.16, 1, 0.3, 1] },
        };

  return (
    <section className="heroi largura" id="instalar">
      <div className="heroi-texto">
        <motion.p className="heroi-selo" {...entrada(0)}>
          Para estudantes do IFMA
        </motion.p>
        <motion.h1 {...entrada(0.06)}>
          Seu SUAP na <span className="destaque">ponta da lingua.</span>
        </motion.h1>
        <motion.p className="heroi-sub" {...entrada(0.12)}>
          O Sabichao conecta seu assistente de IA ao SUAP. Pergunte sobre notas, projetos, relatorios e mais.
        </motion.p>
        <motion.div {...entrada(0.18)}>
          <Instalar aoCopiar={aoCopiar} />
        </motion.div>
      </div>
      <Mascote comemorando={comemorando} />
    </section>
  );
}
