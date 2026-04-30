import React, { useState } from 'react';
import '../styles/character-panel.css';

export type EquipmentType = 'helmet' | 'armor' | 'weapon' | 'shield' | 'boots' | 'ring';

export interface CharacterItem {
  image: string;
  type: EquipmentType;
  aura: number;
}

interface CharacterPanelProps {
  initialInventory?: CharacterItem[];
  initialLevel?: number;
  initialExp?: number;
}

const CharacterPanel: React.FC<CharacterPanelProps> = ({
  initialInventory = [],
  initialLevel = 1,
  initialExp = 0,
}) => {
  const [equipment, setEquipment] = useState<Record<EquipmentType, string | null>>({
    helmet: null,
    armor: null,
    weapon: null,
    shield: null,
    boots: null,
    ring: null,
  });

  const [inventory, setInventory] = useState<CharacterItem[]>(initialInventory);
  const [exp, setExp] = useState(initialExp);
  const [level, setLevel] = useState(initialLevel);

  const equipItem = (item: CharacterItem) => {
    setEquipment((prev) => ({
      ...prev,
      [item.type]: item.image,
    }));
  };

  const consumeItem = (index: number) => {
    const item = inventory[index];
    if (!item) return;

    setExp((prev) => {
      const newExp = prev + item.aura;

      if (newExp >= 100) {
        setLevel((l) => l + 1);
        return newExp - 100;
      }

      return newExp;
    });

    setInventory((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="character-panel">
      <div className="character-header">
        <span>Nivel {level}</span>
      </div>

      <div className="character-body">
        <div className="equipment-grid">
          <div className="slot helmet">
            {equipment.helmet && <img src={equipment.helmet} alt="Helmet" />}
          </div>
          <div className="slot armor">
            {equipment.armor && <img src={equipment.armor} alt="Armor" />}
          </div>
          <div className="slot weapon">
            {equipment.weapon && <img src={equipment.weapon} alt="Weapon" />}
          </div>
          <div className="slot shield">
            {equipment.shield && <img src={equipment.shield} alt="Shield" />}
          </div>
          <div className="slot boots">
            {equipment.boots && <img src={equipment.boots} alt="Boots" />}
          </div>
          <div className="slot ring">
            {equipment.ring && <img src={equipment.ring} alt="Ring" />}
          </div>
        </div>

        <div className="backpack">
          {inventory.map((item, i) => (
            <button
              type="button"
              className="inventory-slot"
              key={`${item.type}-${item.image}-${i}`}
              onClick={() => consumeItem(i)}
              onContextMenu={(e) => {
                e.preventDefault();
                equipItem(item);
              }}
              title="Click: consumir aura | Click derecho: equipar"
            >
              <img src={item.image} alt={item.type} />
            </button>
          ))}
        </div>
      </div>

      <div className="exp-bar">
        <div className="exp-fill" style={{ width: `${exp}%` }} />
      </div>
    </div>
  );
};

export default CharacterPanel;
