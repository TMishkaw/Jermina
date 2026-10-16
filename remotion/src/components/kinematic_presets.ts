/**
 * Kinematic Pose and Motion Cycle Calculations for 2D Stickman
 * All angles in degrees (0 = pointing straight down or neutral).
 */

export interface StickmanPose {
  rootYOffset: number;        // Vertical bounce in pixels
  rootXOffset: number;        // Horizontal sway in pixels
  torsoAngle: number;         // Lean in degrees
  headTilt: number;           // Head tilt in degrees
  
  // Left Arm (degrees)
  leftShoulderAngle: number;
  leftElbowAngle: number;
  
  // Right Arm (degrees)
  rightShoulderAngle: number;
  rightElbowAngle: number;
  
  // Left Leg (degrees)
  leftHipAngle: number;
  leftKneeAngle: number;
  
  // Right Leg (degrees)
  rightHipAngle: number;
  rightKneeAngle: number;
  
  // Talking cadence indicator (0.0 to 1.0)
  talkingCadence: number;
}

export type AnimationType =
  | "idle"
  | "walk"
  | "run"
  | "talk"
  | "point"
  | "point_up"
  | "point_user"
  | "point_to_emoji"
  | "stop"
  | "heart_hands"
  | "watch_time"
  | "shrug"
  | "explain"
  | "surprised"
  | "shocked"
  | "laugh"
  | "jump"
  | "punch"
  | "celebrate";

export function getPoseForFrame(
  animation: AnimationType,
  frame: number,
  fps: number = 30
): StickmanPose {
  const time = frame / fps;
  const twoPi = Math.PI * 2;

  switch (animation) {
    case "walk": {
      // 1.5 steps per second
      const speed = 1.5;
      const phase = time * speed * twoPi;
      const legStride = 28;
      const armSwing = 25;

      // Leg swings
      const leftHip = Math.sin(phase) * legStride;
      const rightHip = Math.sin(phase + Math.PI) * legStride;
      
      // Knee bends more when leg swings forward
      const leftKnee = leftHip < 0 ? Math.abs(Math.sin(phase)) * 25 : 5;
      const rightKnee = rightHip < 0 ? Math.abs(Math.sin(phase + Math.PI)) * 25 : 5;

      // Arms swing opposite to legs
      const leftShoulder = -Math.sin(phase) * armSwing;
      const rightShoulder = -Math.sin(phase + Math.PI) * armSwing;

      // Hip vertical bounce: peaks twice per stride
      const bounce = Math.abs(Math.sin(phase)) * 8;

      return {
        rootYOffset: -bounce,
        rootXOffset: 0,
        torsoAngle: 4, // slight forward lean
        headTilt: -2,
        leftShoulderAngle: leftShoulder,
        leftElbowAngle: 15,
        rightShoulderAngle: rightShoulder,
        rightElbowAngle: 15,
        leftHipAngle: leftHip,
        leftKneeAngle: leftKnee,
        rightHipAngle: rightHip,
        rightKneeAngle: rightKnee,
        talkingCadence: 0,
      };
    }

    case "run": {
      // 2.5 strides per second
      const speed = 2.6;
      const phase = time * speed * twoPi;
      const legStride = 50;
      const armSwing = 55;

      const leftHip = Math.sin(phase) * legStride;
      const rightHip = Math.sin(phase + Math.PI) * legStride;
      const leftKnee = leftHip < 0 ? 55 : 10;
      const rightKnee = rightHip < 0 ? 55 : 10;

      const leftShoulder = -Math.sin(phase) * armSwing;
      const rightShoulder = -Math.sin(phase + Math.PI) * armSwing;

      const bounce = Math.abs(Math.sin(phase)) * 16;

      return {
        rootYOffset: -bounce,
        rootXOffset: 0,
        torsoAngle: 18, // pronounced sprint lean
        headTilt: -5,
        leftShoulderAngle: leftShoulder,
        leftElbowAngle: 65, // running arms bent at 90-ish degrees
        rightShoulderAngle: rightShoulder,
        rightElbowAngle: 65,
        leftHipAngle: leftHip,
        leftKneeAngle: leftKnee,
        rightHipAngle: rightHip,
        rightKneeAngle: rightKnee,
        talkingCadence: 0,
      };
    }

    case "talk": {
      // Natural gesturing: right arm expresses, left arm relaxed
      const gestureSpeed = 1.8;
      const armWave = Math.sin(time * gestureSpeed * twoPi) * 22;
      const forearmWave = Math.cos(time * gestureSpeed * twoPi) * 25;
      const breathing = Math.sin(time * 0.8 * twoPi) * 3;
      const speechSync = (Math.sin(time * 6 * twoPi) + 1) / 2;

      return {
        rootYOffset: breathing,
        rootXOffset: Math.sin(time * 0.4 * twoPi) * 2,
        torsoAngle: 1 + Math.sin(time * 0.8 * twoPi) * 2,
        headTilt: Math.sin(time * 1.2 * twoPi) * 4,
        leftShoulderAngle: -5,
        leftElbowAngle: 10,
        rightShoulderAngle: -35 + armWave,
        rightElbowAngle: 45 + forearmWave,
        leftHipAngle: 0,
        leftKneeAngle: 0,
        rightHipAngle: 5,
        rightKneeAngle: 2,
        talkingCadence: speechSync,
      };
    }

    case "point_up":
    case "point": {
      const breathing = Math.sin(time * 1.0 * twoPi) * 3;
      const pointSway = Math.sin(time * 1.5 * twoPi) * 4;
      const speechSync = (Math.sin(time * 5 * twoPi) + 1) / 2;
      return {
        rootYOffset: breathing,
        rootXOffset: Math.sin(time * 0.5 * twoPi) * 2,
        torsoAngle: 2 + Math.sin(time * 0.8 * twoPi) * 1.5,
        headTilt: 4 + Math.sin(time * 1.2 * twoPi) * 3,
        leftShoulderAngle: -10 + Math.sin(time * 1.1 * twoPi) * 6,
        leftElbowAngle: 25 + Math.sin(time * 1.4 * twoPi) * 10,
        rightShoulderAngle: -80 + pointSway, // dynamic upward/forward point
        rightElbowAngle: 8,   // straight pointing arm with micro-flex
        leftHipAngle: -2,
        leftKneeAngle: 3,
        rightHipAngle: 4,
        rightKneeAngle: 2,
        talkingCadence: speechSync,
      };
    }

    case "point_user": {
      // Directly points index finger at the camera/user with assertive authority
      const nod = Math.sin(time * 2.5 * twoPi) * 3;
      const pulse = Math.sin(time * 3 * twoPi) * 2;
      return {
        rootYOffset: Math.sin(time * 0.8 * twoPi) * 2,
        rootXOffset: 0,
        torsoAngle: 6, // lean toward camera
        headTilt: 2 + nod,
        leftShoulderAngle: 22, // hand confidently placed on hip
        leftElbowAngle: 105,
        rightShoulderAngle: -68 + pulse, // arm aimed straight at viewer
        rightElbowAngle: 4,
        leftHipAngle: -8,
        leftKneeAngle: 10,
        rightHipAngle: 12,
        rightKneeAngle: 14,
        talkingCadence: (Math.sin(time * 6 * twoPi) + 1) / 2,
      };
    }

    case "point_to_emoji": {
      // Looks up and points arm diagonally up towards floating emoji
      const sway = Math.sin(time * 1.2 * twoPi) * 3;
      return {
        rootYOffset: Math.sin(time * 0.7 * twoPi) * 2,
        rootXOffset: -2,
        torsoAngle: -4,
        headTilt: -22, // tilted sharply upward watching the emoji
        leftShoulderAngle: -15,
        leftElbowAngle: 30,
        rightShoulderAngle: -125 + sway, // high diagonal aim
        rightElbowAngle: 10,
        leftHipAngle: -4,
        leftKneeAngle: 6,
        rightHipAngle: 8,
        rightKneeAngle: 4,
        talkingCadence: 0.7,
      };
    }

    case "stop": {
      // Strong defensive STOP gesture: palms raised forward, body braced
      const tension = Math.sin(time * 6 * twoPi) * 1.5;
      return {
        rootYOffset: -2,
        rootXOffset: 0,
        torsoAngle: -7 + tension, // recoil backwards
        headTilt: -2,
        leftShoulderAngle: -75, // both hands thrust forward
        leftElbowAngle: 12,
        rightShoulderAngle: -80,
        rightElbowAngle: 10,
        leftHipAngle: -14, // wide braced stance
        leftKneeAngle: 18,
        rightHipAngle: 14,
        rightKneeAngle: 16,
        talkingCadence: 0.9,
      };
    }

    case "heart_hands": {
      // Both arms arch above head to sculpt a pulsating heart
      const heartbeat = Math.abs(Math.sin(time * 2.5 * twoPi)) * 8;
      const pulseArm = Math.sin(time * 2.5 * twoPi) * 4;
      return {
        rootYOffset: -heartbeat,
        rootXOffset: 0,
        torsoAngle: 0,
        headTilt: -4, // loving upward gaze
        leftShoulderAngle: -135 + pulseArm,
        leftElbowAngle: 80,
        rightShoulderAngle: -135 - pulseArm,
        rightElbowAngle: 80,
        leftHipAngle: -6,
        leftKneeAngle: 6,
        rightHipAngle: 6,
        rightKneeAngle: 6,
        talkingCadence: 0.85,
      };
    }

    case "watch_time": {
      // Checking watch on left wrist, right hand taps wrist
      const tap = Math.sin(time * 5 * twoPi) * 10;
      return {
        rootYOffset: 0,
        rootXOffset: 0,
        torsoAngle: 3,
        headTilt: 16, // looking down at left wrist
        leftShoulderAngle: -42, // wrist held in front of chest
        leftElbowAngle: 90,
        rightShoulderAngle: -35 + tap * 0.4,
        rightElbowAngle: 75 + tap,
        leftHipAngle: -2,
        leftKneeAngle: 4,
        rightHipAngle: 6,
        rightKneeAngle: 6,
        talkingCadence: 0.5,
      };
    }

    case "shrug": {
      // Questioning shrug: raised shoulders, open palms out, head tilted
      const shrugCycle = Math.sin(time * 1.6 * twoPi);
      return {
        rootYOffset: Math.abs(shrugCycle) * 3,
        rootXOffset: 0,
        torsoAngle: 0,
        headTilt: 12 + shrugCycle * 3, // curious head tilt
        leftShoulderAngle: -45 + shrugCycle * 6,
        leftElbowAngle: 90,
        rightShoulderAngle: -45 - shrugCycle * 6,
        rightElbowAngle: 90,
        leftHipAngle: -4,
        leftKneeAngle: 4,
        rightHipAngle: 4,
        rightKneeAngle: 4,
        talkingCadence: 0.7,
      };
    }

    case "explain": {
      // Flowing two-handed conversational explanation
      const waveL = Math.sin(time * 2.0 * twoPi) * 15;
      const waveR = Math.cos(time * 2.0 * twoPi) * 15;
      return {
        rootYOffset: Math.sin(time * 0.9 * twoPi) * 2,
        rootXOffset: Math.sin(time * 0.5 * twoPi) * 2,
        torsoAngle: Math.sin(time * 0.8 * twoPi) * 2,
        headTilt: Math.sin(time * 1.4 * twoPi) * 3,
        leftShoulderAngle: -30 + waveL,
        leftElbowAngle: 50 + waveL * 0.5,
        rightShoulderAngle: -35 + waveR,
        rightElbowAngle: 50 + waveR * 0.5,
        leftHipAngle: -2,
        leftKneeAngle: 3,
        rightHipAngle: 3,
        rightKneeAngle: 2,
        talkingCadence: (Math.sin(time * 6 * twoPi) + 1) / 2,
      };
    }

    case "jump": {
      // 1.5s loop: crouch (0.0-0.3) -> leap (0.3-0.8) -> peak (0.8-1.1) -> land (1.1-1.5)
      const loopTime = time % 1.5;
      let yOff = 0;
      let knee = 0;
      let armAngle = 0;

      if (loopTime < 0.3) {
        // Crouch prep
        const p = loopTime / 0.3;
        yOff = p * 20;
        knee = p * 40;
        armAngle = p * 30; // arms swing back
      } else if (loopTime < 0.7) {
        // Leap
        const p = (loopTime - 0.3) / 0.4;
        yOff = 20 - p * 80; // launching upwards
        knee = (1 - p) * 30;
        armAngle = -80 * p; // arms throw up
      } else if (loopTime < 1.1) {
        // Falling
        const p = (loopTime - 0.7) / 0.4;
        yOff = -60 + p * 60;
        knee = 20 * p;
        armAngle = -80 + p * 60;
      } else {
        // Impact cushion
        const p = (loopTime - 1.1) / 0.4;
        yOff = (1 - p) * 15;
        knee = (1 - p) * 30;
        armAngle = 0;
      }

      return {
        rootYOffset: yOff,
        rootXOffset: 0,
        torsoAngle: -5,
        headTilt: -5,
        leftShoulderAngle: armAngle,
        leftElbowAngle: 15,
        rightShoulderAngle: armAngle,
        rightElbowAngle: 15,
        leftHipAngle: knee * 0.5,
        leftKneeAngle: knee,
        rightHipAngle: knee * 0.5,
        rightKneeAngle: knee,
        talkingCadence: 0,
      };
    }

    case "punch": {
      // Quick jab cross cycle (0.8s)
      const punchCycle = (time % 0.8) / 0.8;
      let rightArmS = -10;
      let rightArmE = 80;
      let torsoLean = 0;

      if (punchCycle < 0.3) {
        // Windup
        rightArmS = -10;
        rightArmE = 95;
      } else if (punchCycle < 0.5) {
        // Strike extension
        const p = (punchCycle - 0.3) / 0.2;
        rightArmS = -85 * p;
        rightArmE = 5;
        torsoLean = 10 * p;
      } else {
        // Retract
        const p = (punchCycle - 0.5) / 0.3;
        rightArmS = -85 * (1 - p);
        rightArmE = 5 + 75 * p;
        torsoLean = 10 * (1 - p);
      }

      return {
        rootYOffset: 0,
        rootXOffset: 0,
        torsoAngle: torsoLean,
        headTilt: 0,
        leftShoulderAngle: -40, // guard position
        leftElbowAngle: 90,
        rightShoulderAngle: rightArmS,
        rightElbowAngle: rightArmE,
        leftHipAngle: -12,
        leftKneeAngle: 15,
        rightHipAngle: 14,
        rightKneeAngle: 20,
        talkingCadence: 0,
      };
    }

    case "surprised":
    case "shocked": {
      // Dynamic recoil and gasping shock
      const jitter = (Math.sin(time * 12 * twoPi)) * 3;
      return {
        rootYOffset: jitter - 6,
        rootXOffset: Math.sin(time * 6 * twoPi) * 2,
        torsoAngle: -8,
        headTilt: -6 + Math.sin(time * 3 * twoPi) * 4,
        leftShoulderAngle: -100 + jitter * 2,
        leftElbowAngle: 85,
        rightShoulderAngle: -100 - jitter * 2,
        rightElbowAngle: 85,
        leftHipAngle: -8,
        leftKneeAngle: 14,
        rightHipAngle: 8,
        rightKneeAngle: 14,
        talkingCadence: 0.9,
      };
    }

    case "laugh": {
      // Organic laughter bounce and head nod
      const laughBounce = Math.abs(Math.sin(time * 3.5 * twoPi)) * 9;
      const headNod = Math.sin(time * 3.5 * twoPi) * 8;
      const armJiggle = Math.sin(time * 3.5 * twoPi) * 14;
      return {
        rootYOffset: -laughBounce,
        rootXOffset: 0,
        torsoAngle: 4 + Math.sin(time * 1.5 * twoPi) * 3,
        headTilt: -4 + headNod,
        leftShoulderAngle: -20 + armJiggle * 0.5,
        leftElbowAngle: 35,
        rightShoulderAngle: -45 + armJiggle,
        rightElbowAngle: 60,
        leftHipAngle: -4,
        leftKneeAngle: 6,
        rightHipAngle: 6,
        rightKneeAngle: 8,
        talkingCadence: (Math.sin(time * 7 * twoPi) + 1) / 2,
      };
    }

    case "celebrate": {
      const cheerSpeed = 3.0;
      const cheerWave = Math.sin(time * cheerSpeed * twoPi) * 25;
      const bounce = Math.abs(Math.sin(time * cheerSpeed * twoPi)) * 12;

      return {
        rootYOffset: -bounce,
        rootXOffset: 0,
        torsoAngle: 0,
        headTilt: -8, // looking up excitedly
        leftShoulderAngle: -130 + cheerWave,
        leftElbowAngle: 20,
        rightShoulderAngle: -130 - cheerWave,
        rightElbowAngle: 20,
        leftHipAngle: -8,
        leftKneeAngle: 8,
        rightHipAngle: 8,
        rightKneeAngle: 8,
        talkingCadence: 0.8,
      };
    }

    case "idle":
    default: {
      const breathing = Math.sin(time * 0.9 * twoPi) * 3.5;
      const gentleSway = Math.sin(time * 0.45 * twoPi) * 3;
      return {
        rootYOffset: breathing,
        rootXOffset: gentleSway,
        torsoAngle: Math.sin(time * 0.5 * twoPi) * 1.5,
        headTilt: Math.sin(time * 0.7 * twoPi) * 3,
        leftShoulderAngle: -8 + Math.sin(time * 0.9 * twoPi) * 4,
        leftElbowAngle: 15,
        rightShoulderAngle: -8 - Math.sin(time * 0.9 * twoPi) * 4,
        rightElbowAngle: 15,
        leftHipAngle: -2,
        leftKneeAngle: 3,
        rightHipAngle: 2,
        rightKneeAngle: 3,
        talkingCadence: 0.35,
      };
    }
  }
}
