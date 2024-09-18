import React, { useState } from "react";
import "@pixi/events";
import { Stage, Container, Graphics, Text } from "@pixi/react";
import * as PIXI from "pixi.js";
import _ from "lodash";
import io from "socket.io-client";
import { Modal, Button } from "react-bootstrap";

const HEX_RADIUS = 80;

// Hardcoded coordinates for each hex
const HEX_POSITIONS = [
    // Row 1
    { x: -Math.sqrt(3) * HEX_RADIUS, y: -3 * HEX_RADIUS },
    { x: 0, y: -3 * HEX_RADIUS },
    { x: Math.sqrt(3) * HEX_RADIUS, y: -3 * HEX_RADIUS },
    // Row 2
    { x: -1.5 * Math.sqrt(3) * HEX_RADIUS, y: -1.5 * HEX_RADIUS },
    { x: -0.5 * Math.sqrt(3) * HEX_RADIUS, y: -1.5 * HEX_RADIUS },
    { x: 0.5 * Math.sqrt(3) * HEX_RADIUS, y: -1.5 * HEX_RADIUS },
    { x: 1.5 * Math.sqrt(3) * HEX_RADIUS, y: -1.5 * HEX_RADIUS },
    // Row 3
    { x: -2 * Math.sqrt(3) * HEX_RADIUS, y: 0 },
    { x: -Math.sqrt(3) * HEX_RADIUS, y: 0 },
    { x: 0, y: 0 },
    { x: Math.sqrt(3) * HEX_RADIUS, y: 0 },
    { x: 2 * Math.sqrt(3) * HEX_RADIUS, y: 0 },
    // Row 4
    { x: -1.5 * Math.sqrt(3) * HEX_RADIUS, y: 1.5 * HEX_RADIUS },
    { x: -0.5 * Math.sqrt(3) * HEX_RADIUS, y: 1.5 * HEX_RADIUS },
    { x: 0.5 * Math.sqrt(3) * HEX_RADIUS, y: 1.5 * HEX_RADIUS },
    { x: 1.5 * Math.sqrt(3) * HEX_RADIUS, y: 1.5 * HEX_RADIUS },
    // Row 5
    { x: -Math.sqrt(3) * HEX_RADIUS, y: 3 * HEX_RADIUS },
    { x: 0, y: 3 * HEX_RADIUS },
    { x: Math.sqrt(3) * HEX_RADIUS, y: 3 * HEX_RADIUS },
];

// Coordinates for settlement vertices based on hardcoded hex locations
const VERTEX_POSITIONS = [];
// Map between index of a hex and the indices of its vertices
const VERTEX_ADJACENCIES = {};
for (let i = 0; i < HEX_POSITIONS.length; i++) {
    VERTEX_ADJACENCIES[i] = [];

    // Calculate vertices of hexagon
    for (let j = 0; j < 6; j++) {
        const angle = (j * 60 + 30) * (Math.PI / 180); // 30 degrees offset to make it vertical
        const point = {
            x: HEX_POSITIONS[i].x + HEX_RADIUS * Math.cos(angle),
            y: HEX_POSITIONS[i].y + HEX_RADIUS * Math.sin(angle),
        };
        // Check if vertex position is already in list using approximation
        if (
            !_.some(
                VERTEX_POSITIONS,
                (vertex) =>
                    Math.abs(vertex.x - point.x) +
                        Math.abs(vertex.y - point.y) <
                    1e-5
            )
        ) {
            VERTEX_POSITIONS.push(point);
        }
        // Check if vertex position is already in list using approximation
        VERTEX_ADJACENCIES[i].push(
            _.findIndex(
                VERTEX_POSITIONS,
                (vertex) =>
                    Math.abs(vertex.x - point.x) +
                        Math.abs(vertex.y - point.y) <
                    1e-5
            )
        );
    }
}

const SETTLEMENT_SIZE = 15;
const CITY_SIZE = 20;

const socket = io();

const placeSettlement = (vertexIndex) => {
    socket.emit("place_settlement", { vertexIndex });
};

const upgradeToCity = (vertexIndex) => {
    socket.emit("upgrade_to_city", { vertexIndex });
};

const CatanBoard = ({ gameState, username }) => {
    let board = gameState.board;
    let hexes = board.hexes.map((hex, index) => (
        <Container
            key={`hex-${index}`}
            x={HEX_POSITIONS[index].x}
            y={HEX_POSITIONS[index].y}
        >
            <Hexagon resource={hex.resource} />
            {hex.number && <HexNumber number={hex.number} />}
        </Container>
    ));

    let vertices = board.vertices.map((vertex, index) => (
        <Vertex
            key={`vertex-${index}`}
            x={VERTEX_POSITIONS[vertex.position].x}
            y={VERTEX_POSITIONS[vertex.position].y}
            color={
                vertex.playerName
                    ? _.find(gameState.players, { name: vertex.playerName })
                          .color
                    : 0xffffff
            }
            isOccupied={!!vertex.playerName}
            isCity={vertex.upgraded}
            vertexIndex={index}
            gameState={gameState}
            clickable={
                username === gameState.playerTurn &&
                (username === vertex.playerName || !vertex.playerName)
            }
        />
    ));
    return (
        <Stage
            width={1200}
            height={800}
            options={{ backgroundColor: 0x1099bb }}
        >
            <Container x={600} y={400}>
                {hexes}
            </Container>
            <Container x={600} y={400}>
                {vertices}
            </Container>
        </Stage>
    );
};

const Hexagon = ({ resource }) => {
    return (
        <Graphics
            draw={(g) => {
                g.clear();
                g.lineStyle(2, 0x000000, 1); // width: 2, color: black, alpha: 1
                g.beginFill(getHexColor(resource));
                // Calculate the coordinates for a vertical hexagon
                const verticalHexPoints = [];
                for (let i = 0; i < 6; i++) {
                    const angle = (i * 60 + 30) * (Math.PI / 180); // 30 degrees offset to make it vertical
                    verticalHexPoints.push(
                        HEX_RADIUS * Math.cos(angle),
                        HEX_RADIUS * Math.sin(angle)
                    );
                }
                g.drawPolygon(verticalHexPoints);
                g.endFill();
            }}
        />
    );
};

const HexNumber = ({ number }) => {
    return (
        <Text
            text={number.toString()}
            anchor={0.5}
            style={
                new PIXI.TextStyle({
                    fontFamily: "Arial",
                    fontSize: 24,
                    fill: 0xffffff,
                    align: "center",
                })
            }
        />
    );
};

function getHexColor(resource) {
    const colorMap = {
        wood: 0x228b22,
        brick: 0x8b4513,
        sheep: 0x90ee90,
        wheat: 0xffd700,
        ore: 0x708090,
        desert: 0xf4a460,
    };
    return colorMap[resource] || 0xffffff;
}

const Vertex = ({
    x,
    y,
    color,
    isOccupied,
    isCity,
    clickable,
    vertexIndex,
    gameState,
}) => {
    const [showModal, setShowModal] = useState(false);

    const handleClick = () => {
        console.log(canPlaceSettlement());
        if (isOccupied) {
            if (!isCity && canUpgradeToCity()) {
                setShowModal(true);
            }
        } else if (canPlaceSettlement()) {
            setShowModal(true);
        }
    };

    const canUpgradeToCity = () => {
        return (
            gameState.currentTurn < 2 * gameState.players.length ||
            (gameState.resources.ore >= 3 && gameState.resources.wheat >= 2)
        );
    };

    const canPlaceSettlement = () => {
        return (
            gameState.currentTurn < 2 * gameState.players.length ||
            (gameState.resources.wood >= 1 &&
                gameState.resources.brick >= 1 &&
                gameState.resources.wheat >= 1 &&
                gameState.resources.sheep >= 1)
        );
    };

    const handleConfirm = () => {
        if (isOccupied && !isCity) {
            upgradeToCity(vertexIndex);
        } else {
            placeSettlement(vertexIndex);
        }
        setShowModal(false);
    };

    return (
        <>
            <Graphics
                x={x}
                y={y}
                interactive={true}
                buttonMode={true}
                onClick={() => {
                    console.log("HIHIHIHIH");
                }}
                mousemove={() => {
                    console.log("HIHIHIHIH");
                }}
                mousedown={() => {
                    console.log("HIHIHIHIH");
                }}
                click={() => {
                    console.log("HIHIHIHIH");
                }}
                draw={(g) => {
                    g.clear();
                    if (isOccupied) {
                        g.beginFill(color);
                        if (isCity) {
                            g.drawRect(
                                -CITY_SIZE / 2,
                                -CITY_SIZE / 2,
                                CITY_SIZE,
                                CITY_SIZE
                            );
                        } else {
                            g.drawRect(
                                -SETTLEMENT_SIZE / 2,
                                -SETTLEMENT_SIZE / 2,
                                SETTLEMENT_SIZE,
                                SETTLEMENT_SIZE
                            );
                        }
                        g.endFill();
                    } else if (clickable) {
                        g.lineStyle(2, 0xffffff);
                        g.drawCircle(0, 0, 5);
                    }
                }}
            />
            <Modal show={showModal} onHide={() => setShowModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>
                        {isOccupied ? "Upgrade to City" : "Place Settlement"}
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    Are you sure you want to{" "}
                    {isOccupied
                        ? "upgrade this settlement to a city"
                        : "place a settlement here"}
                    ?
                </Modal.Body>
                <Modal.Footer>
                    <Button
                        variant="secondary"
                        onClick={() => setShowModal(false)}
                    >
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleConfirm}>
                        Confirm
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

export default CatanBoard;
