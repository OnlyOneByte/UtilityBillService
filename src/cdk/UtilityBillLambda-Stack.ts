
import { Construct } from 'constructs';
import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { execSync } from 'child_process';
import lambda = require('aws-cdk-lib/aws-lambda');


export class UtilityBillLambdaStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'UtilityBillGettQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });

    const pythonLambdaFunction = new lambda.Function(this, 'python-lambda', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'pyLambda.handler',
      code: lambda.Code.fromAsset('./src/lambda', {
        bundling: {
          image: lambda.Runtime.PYTHON_3_9.bundlingImage,
          command: [],
          local: {
            tryBundle(outputDir: string) {
              try {
                execSync('pip3 --version');
              } catch {
                return false;
              }

              const commands = [
                `cd src/lambda`,
                `pip3 install -r requirements.txt -t ${outputDir}`,
                `cp -a . ${outputDir}`
              ];

              execSync(commands.join(' && '));
              return true;
            }
          }
        }
      }),
      memorySize: 1024,
      functionName: 'UtilityBillHandler',
      timeout: Duration.seconds(300)
    });
    
  }
}
