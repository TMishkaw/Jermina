import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { FacialExpressions, EyeExpression, MouthExpression } from "./FacialExpressions";
import { getPoseForFrame, AnimationType, StickmanPose } from "./kinematic_presets";

export interface StickmanRigProps {
  animation?: AnimationType;
  customPose?: Partial<StickmanPose>;
  eyeType?: EyeExpression;
  mouthType?: MouthExpression;
  x?: number;
  y?: number;
  scale?: number;
  color?: string;
  glowColor?: string;
  strokeWidth?: number;
  headRadius?: number;
  torsoLength?: number;
  limbLength?: number;
  prop?: "microphone" | "sword" | "coffee" | "laptop" | "heart" | "stop_sign" | "watch" | "none";
}

export const StickmanRig: React.FC<StickmanRigProps> = ({
  animation = "idle",
  customPose,
  eyeType = "neutral",
  mouthType = "neutral",
  x = 540,
  y = 960,
  scale = 1.0,
  color = "#FFFFFF",
  glowColor = "#00FFFF",
  strokeWidth = 6,
  headRadius = 32,
  torsoLength = 90,
  limbLength = 55,
  prop = "none",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Compute calculated kinematic pose for the current frame
  const computedPose = getPoseForFrame(animation, frame, fps);
  const pose: StickmanPose = { ...computedPose, ...customPose };

  const rootY = y + pose.rootYOffset;
  const rootX = x + pose.rootXOffset;

  // Filter for glow styling
  const glowFilter = glowColor
    ? `drop-shadow(0px 0px 8px ${glowColor}) drop-shadow(0px 0px 20px ${glowColor}66)`
    : "none";

  // Limb forward kinematics helper: returns end point of a rotated segment
  const getSegmentEnd = (startX: number, startY: number, length: number, angleDeg: number) => {
    const rad = (angleDeg * Math.PI) / 180;
    return {
      x: startX + Math.sin(rad) * length,
      y: startY + Math.cos(rad) * length,
    };
  };

  // Shoulder and Hip anchor points
  const shoulderY = -torsoLength * 0.85;
  const hipY = 0; // Hips are at root (0, 0)
  const headY = shoulderY - headRadius - 6;

  // Arms Forward Kinematics
  // Left Arm
  const leftElbow = getSegmentEnd(0, shoulderY, limbLength, pose.leftShoulderAngle);
  const leftHand = getSegmentEnd(leftElbow.x, leftElbow.y, limbLength, pose.leftShoulderAngle + pose.leftElbowAngle);

  // Right Arm
  const rightElbow = getSegmentEnd(0, shoulderY, limbLength, pose.rightShoulderAngle);
  const rightHand = getSegmentEnd(rightElbow.x, rightElbow.y, limbLength, pose.rightShoulderAngle + pose.rightElbowAngle);

  // Legs Forward Kinematics
  // Left Leg
  const leftKnee = getSegmentEnd(-10, hipY, limbLength, pose.leftHipAngle);
  const leftFoot = getSegmentEnd(leftKnee.x, leftKnee.y, limbLength, pose.leftHipAngle + pose.leftKneeAngle);

  // Right Leg
  const rightKnee = getSegmentEnd(10, hipY, limbLength, pose.rightHipAngle);
  const rightFoot = getSegmentEnd(rightKnee.x, rightKnee.y, limbLength, pose.rightHipAngle + pose.rightKneeAngle);

  // Render optional accessories/props in right hand or scene
  const renderProp = () => {
    switch (prop) {
      case "microphone":
        return (
          <g transform={`translate(${rightHand.x}, ${rightHand.y})`}>
            <line x1={0} y1={0} x2={8} y2={18} stroke="#444" strokeWidth={strokeWidth} strokeLinecap="round" />
            <circle cx={-2} cy={-4} r={7} fill="#888" stroke="#AAA" strokeWidth={2} />
          </g>
        );
      case "sword":
        return (
          <g transform={`translate(${rightHand.x}, ${rightHand.y}) rotate(-45)`}>
            <line x1={0} y1={-80} x2={0} y2={10} stroke="#00FFFF" strokeWidth={strokeWidth - 1} strokeLinecap="round" />
            <line x1={-12} y1={0} x2={12} y2={0} stroke="#FFCC00" strokeWidth={strokeWidth} strokeLinecap="round" />
          </g>
        );
      case "coffee":
        return (
          <g transform={`translate(${rightHand.x + 6}, ${rightHand.y - 4})`}>
            <rect x={-8} y={-10} width={16} height={20} rx={3} fill="#DDD" stroke={color} strokeWidth={2} />
            <path d="M 0 -14 Q 3 -18 0 -22" stroke="#FFF" strokeWidth={2} fill="none" opacity={0.7} />
          </g>
        );
      case "laptop":
        return (
          <g transform={`translate(${rightHand.x - 8}, ${rightHand.y - 10})`}>
            <rect x={-14} y={-4} width={28} height={16} rx={2} fill="#1E293B" stroke={glowColor} strokeWidth={2} />
            <rect x={-12} y={-16} width={24} height={13} rx={2} fill="#0F172A" stroke={glowColor} strokeWidth={1.5} />
            <line x1={-8} y1={-10} x2={6} y2={-10} stroke={glowColor} strokeWidth={1.5} />
            <line x1={-8} y1={-6} x2={2} y2={-6} stroke="#38BDF8" strokeWidth={1.5} />
          </g>
        );
      case "heart":
        return (
          <g transform={`translate(0, ${headY - headRadius - 16}) scale(${1 + Math.sin(frame * 0.25) * 0.15})`}>
            <path
              d="M 0 -6 C -8 -20, -22 -4, 0 14 C 22 -4, 8 -20, 0 -6 Z"
              fill="#FF007F"
              stroke="#FFFFFF"
              strokeWidth={2}
              style={{ filter: "drop-shadow(0px 0px 8px #FF007F)" }}
            />
          </g>
        );
      case "stop_sign":
        return (
          <g transform={`translate(${rightHand.x + 12}, ${rightHand.y - 12})`}>
            <polygon points="-12,-6 -6,-12 6,-12 12,-6 12,6 6,12 -6,12 -12,6" fill="#EF4444" stroke="#FFFFFF" strokeWidth={2} />
            <text x={0} y={4} fill="#FFFFFF" fontSize={7} fontWeight="900" textAnchor="middle" fontFamily="sans-serif">STOP</text>
          </g>
        );
      case "watch":
        return (
          <g transform={`translate(${leftHand.x}, ${leftHand.y})`}>
            <circle cx={0} cy={0} r={6} fill="#0F172A" stroke={glowColor} strokeWidth={2} />
            <circle cx={0} cy={0} r={2} fill={glowColor} />
          </g>
        );
      case "none":
      default:
        return null;
    }
  };

  return (
    <g
      id="stickman-root"
      transform={`translate(${rootX}, ${rootY}) scale(${scale})`}
      style={{ filter: glowFilter }}
    >
      {/* Torso & Head with torso tilt */}
      <g transform={`rotate(${pose.torsoAngle}, 0, ${hipY})`}>
        {/* Head */}
        <g transform={`translate(0, ${headY}) rotate(${pose.headTilt})`}>
          <circle
            cx={0}
            cy={0}
            r={headRadius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="#111116"
          />
          <FacialExpressions
            eyeType={eyeType}
            mouthType={mouthType === "talking" ? "talking" : mouthType}
            headRadius={headRadius}
            color={color}
            strokeWidth={Math.max(2, strokeWidth * 0.5)}
            talkingOffset={pose.talkingCadence}
          />
        </g>

        {/* Neck connector */}
        <line
          x1={0}
          y1={headY + headRadius}
          x2={0}
          y2={shoulderY}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Torso Spine */}
        <line
          x1={0}
          y1={shoulderY}
          x2={0}
          y2={hipY}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Left Arm (behind body in 2.5D layering) */}
        <g id="left-arm">
          <line
            x1={0}
            y1={shoulderY}
            x2={leftElbow.x}
            y2={leftElbow.y}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          <line
            x1={leftElbow.x}
            y1={leftElbow.y}
            x2={leftHand.x}
            y2={leftHand.y}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          <circle cx={leftHand.x} cy={leftHand.y} r={strokeWidth * 0.7} fill={color} />
        </g>

        {/* Right Arm (in front of body) */}
        <g id="right-arm">
          <line
            x1={0}
            y1={shoulderY}
            x2={rightElbow.x}
            y2={rightElbow.y}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          <line
            x1={rightElbow.x}
            y1={rightElbow.y}
            x2={rightHand.x}
            y2={rightHand.y}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          <circle cx={rightHand.x} cy={rightHand.y} r={strokeWidth * 0.7} fill={color} />
          {renderProp()}
          {/* Automatic glowing heart between hands during heart_hands */}
          {animation === "heart_hands" && prop !== "heart" && (
            <g transform={`translate(0, ${headY - headRadius - 16}) scale(${1 + Math.sin(frame * 0.25) * 0.15})`}>
              <path
                d="M 0 -6 C -8 -20, -22 -4, 0 14 C 22 -4, 8 -20, 0 -6 Z"
                fill="#FF007F"
                stroke="#FFFFFF"
                strokeWidth={2}
                style={{ filter: "drop-shadow(0px 0px 10px #FF007F)" }}
              />
            </g>
          )}
          {/* Automatic STOP sign badge during stop */}
          {animation === "stop" && prop !== "stop_sign" && (
            <g transform={`translate(${rightHand.x + 10}, ${rightHand.y - 10})`}>
              <polygon points="-10,-5 -5,-10 5,-10 10,-5 10,5 5,10 -5,10 -10,5" fill="#EF4444" stroke="#FFFFFF" strokeWidth={1.5} />
              <text x={0} y={3} fill="#FFFFFF" fontSize={6} fontWeight="900" textAnchor="middle" fontFamily="sans-serif">STOP</text>
            </g>
          )}
        </g>
      </g>

      {/* Pelvis bar */}
      <line
        x1={-12}
        y1={hipY}
        x2={12}
        y2={hipY}
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
      />

      {/* Left Leg */}
      <g id="left-leg">
        <line
          x1={-10}
          y1={hipY}
          x2={leftKnee.x}
          y2={leftKnee.y}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        <line
          x1={leftKnee.x}
          y1={leftKnee.y}
          x2={leftFoot.x}
          y2={leftFoot.y}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        <line
          x1={leftFoot.x}
          y1={leftFoot.y}
          x2={leftFoot.x + 12}
          y2={leftFoot.y}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
      </g>

      {/* Right Leg */}
      <g id="right-leg">
        <line
          x1={10}
          y1={hipY}
          x2={rightKnee.x}
          y2={rightKnee.y}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        <line
          x1={rightKnee.x}
          y1={rightKnee.y}
          x2={rightFoot.x}
          y2={rightFoot.y}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        <line
          x1={rightFoot.x}
          y1={rightFoot.y}
          x2={rightFoot.x + 12}
          y2={rightFoot.y}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
      </g>
    </g>
  );
};
