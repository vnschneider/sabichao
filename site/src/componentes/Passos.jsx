import { motion, useReducedMotion } from "motion/react";
import { DownloadSimple, Key, ChatCircleDots, MagnifyingGlass } from "@phosphor-icons/react";
import { PASSOS } from "../conteudo.js";
import "./Passos.css";

const ICONES = { instalar: DownloadSimple, logar: Key, perguntar: ChatCircleDots, consultar: MagnifyingGlass };

export default function Passos() {
  const reduzir = useReducedMotion();
  return (
    <section className="secao passos" id="como">
      <div className="largura">
        <h2 className="secao-titulo">Como funciona</h2>
        <p className="secao-sub">Instale, logue, pergunte. O Sabichao faz o resto.</p>
        <ol className="passos-trilha">
          {PASSOS.map((passo, i) => {
            const Icone = ICONES[passo.icone];
            return (
              <motion.li
                key={passo.titulo}
                initial={reduzir ? false : { opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.4 }}
                transition={{ duration: 0.6, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
              >
                <span className="passos-icone">
                  <Icone size={24} weight="duotone" />
                </span>
                <h3>{passo.titulo}</h3>
                <p>{passo.texto}</p>
              </motion.li>
            );
          })}
        </ol>
      </div>
    </section>
  );
}
