import { CloudSlash, EyeSlash, Password } from "@phosphor-icons/react";
import { GARANTIAS } from "../conteudo.js";
import "./Garantias.css";

const ICONES = { senha: Password, leitura: EyeSlash, dados: CloudSlash };

export default function Garantias() {
  return (
    <section className="secao garantias" id="seguranca">
      <div className="largura garantias-grade">
        <h2 className="garantias-frase">
          Seus dados continuam <span>seus</span>.
        </h2>
        <ul className="garantias-lista">
          {GARANTIAS.map((g) => {
            const Icone = ICONES[g.icone];
            return (
              <li key={g.titulo}>
                <Icone size={28} weight="duotone" />
                <div>
                  <h3>{g.titulo}</h3>
                  <p>{g.texto}</p>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
