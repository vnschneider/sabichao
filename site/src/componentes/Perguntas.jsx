import { Plus } from "@phosphor-icons/react";
import { PERGUNTAS } from "../conteudo.js";
import "./Perguntas.css";

export default function Perguntas() {
  return (
    <section className="secao perguntas" id="perguntas">
      <div className="largura perguntas-grade">
        <h2 className="secao-titulo">Perguntas frequentes</h2>
        <div className="perguntas-lista">
          {PERGUNTAS.map((p) => (
            <details key={p.pergunta}>
              <summary>
                {p.pergunta}
                <Plus size={20} weight="bold" aria-hidden="true" />
              </summary>
              <p>{p.resposta}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
