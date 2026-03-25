'use client';

import { useEffect, useRef } from 'react';
import { AgentStatus } from '@/types/agent';

interface AgentAvatarProps {
  emoji: string;
  status: AgentStatus;
  color: string;
}

export default function AgentAvatar({ emoji, status, color }: AgentAvatarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrame: number;
    let startTime = Date.now();

    const draw = () => {
      const elapsed = (Date.now() - startTime) / 1000;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Background circle with color
      ctx.beginPath();
      ctx.arc(50, 50, 40, 0, Math.PI * 2);
      ctx.fillStyle = color;
      
      // Apply status-based effects
      switch (status) {
        case 'idle':
          // Breathing effect
          const breathScale = 1 + Math.sin(elapsed * 2) * 0.05;
          ctx.globalAlpha = 0.8 + Math.sin(elapsed * 2) * 0.2;
          ctx.scale(breathScale, breathScale);
          ctx.translate((50 * (1 - breathScale)), (50 * (1 - breathScale)));
          break;
        case 'working':
          // Pulsing glow
          const glowIntensity = 0.5 + Math.sin(elapsed * 4) * 0.5;
          ctx.shadowBlur = 20 * glowIntensity;
          ctx.shadowColor = color;
          break;
        case 'complete':
          // Bright glow
          ctx.shadowBlur = 25;
          ctx.shadowColor = color;
          ctx.globalAlpha = 1;
          break;
        case 'error':
          // Red pulse
          const pulseAlpha = 0.5 + Math.sin(elapsed * 6) * 0.3;
          ctx.globalAlpha = pulseAlpha;
          break;
      }

      ctx.fill();
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalAlpha = 1;
      ctx.shadowBlur = 0;

      // Emoji
      ctx.font = '48px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#ffffff';
      
      // Typing animation for working status
      if (status === 'working') {
        const bounce = Math.sin(elapsed * 8) * 3;
        ctx.fillText(emoji, 50, 50 + bounce);
      } else {
        ctx.fillText(emoji, 50, 50);
      }

      // Status indicator overlays
      if (status === 'complete') {
        // Checkmark
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(70, 30);
        ctx.lineTo(75, 35);
        ctx.lineTo(85, 25);
        ctx.stroke();
      } else if (status === 'error') {
        // X mark
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(70, 25);
        ctx.lineTo(80, 35);
        ctx.moveTo(80, 25);
        ctx.lineTo(70, 35);
        ctx.stroke();
      } else if (status === 'working') {
        // Spinner dots
        for (let i = 0; i < 3; i++) {
          const dotAngle = (elapsed * 3 + i * (Math.PI * 2 / 3)) % (Math.PI * 2);
          const x = 75 + Math.cos(dotAngle) * 8;
          const y = 30 + Math.sin(dotAngle) * 8;
          ctx.beginPath();
          ctx.arc(x, y, 2, 0, Math.PI * 2);
          ctx.fillStyle = '#3b82f6';
          ctx.fill();
        }
      }

      animationFrame = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [emoji, status, color]);

  return (
    <canvas
      ref={canvasRef}
      width={100}
      height={100}
      className="w-24 h-24"
    />
  );
}
