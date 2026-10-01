import { motion, useReducedMotion } from "motion/react";
import { ChartBar, Notebook, FileText, GraduationCap } from "@phosphor-icons/react";
import { RECURSOS } from "../conteudo.js";
import "./Recursos.css";

const ICONES = { notas: ChartBar, projetos: Notebook, relatorios: FileText, matricula: GraduationCap };

export default function Recursos() {
  const reduzir = useReducedMotion();
  return (
    <section className="secao recursos" id="recursos">
      <div className="largura">
        <h2 className="secao-titulo">Tudo do SUAP, numa conversa</h2>
        <p className="secao-sub">
          Pergunte no seu assistente de IA e o Sabichao busca direto no SUAP.
        </p>
        <ul className="recursos-grade">
          {RECURSOS.map((r, i) => {
            const Icone = ICONES[r.icone];
            return (
              <motion.li
                key={r.titulo}
                initial={reduzir ? false : { opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.4 }}
                transition={{ duration: 0.6, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
              >
                <span className="recursos-icone">
                  <Icone size={26} weight="duotone" />
                </span>
                <h3>{r.titulo}</h3>
                <p>{r.texto}</p>
              </motion.li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
